import base64
import hashlib
import hmac
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal, TypeVar

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field

from api.dependencies.security import OrgSystemStorageDep
from core.domain.errors import InternalError
from core.storage.organization_storage import OrganizationSystemStorage

router = APIRouter(prefix="/webhooks/clerk", include_in_schema=False)
_logger = logging.getLogger(__name__)


class _WebhookVerificationError(ValueError):
    pass


def _verify_timestamp(timestamp_header: str):
    webhook_tolerance = timedelta(minutes=5)
    now = datetime.now(tz=timezone.utc)
    try:
        timestamp = datetime.fromtimestamp(float(timestamp_header), tz=timezone.utc)
    except Exception:
        raise _WebhookVerificationError("Invalid Signature Headers")

    if abs(now - timestamp) > webhook_tolerance:
        raise _WebhookVerificationError("Message timestamp too old")


_T = TypeVar("_T", bound=BaseModel)


class _ClerkWebhookSigner:
    def __init__(self, raw: str):
        if not raw:
            raise ValueError("Missing clerk webhook secret")
        signer = raw.split("_")
        if not len(signer) == 2:
            _logger.warning("Invalid CLERK_WEBHOOKS_SECRET")
            return
        self._secret = base64.b64decode(signer[1])

    def _compute_signature(self, id: str, timestamp: str, body: str):
        signedContent = f"{id}.{timestamp}.{body}".encode()
        return hmac.new(self._secret, signedContent, hashlib.sha256).digest()

    def verify_signature(self, id: str, timestamp: str, body: str, signatures: str, model: type[_T]) -> _T:
        signed_bytes = self._compute_signature(id, timestamp, body)

        for versioned in signatures.split(" "):
            (version, signature) = versioned.split(",")
            if version != "v1":
                continue
            sig_bytes = base64.b64decode(signature)
            if hmac.compare_digest(signed_bytes, sig_bytes):
                return model.model_validate_json(body)
        raise _WebhookVerificationError("Invalid signature")

    async def verify_webhook(self, request: Request, returns: type[_T]) -> _T:
        svix_id = request.headers.get("svix-id")
        svix_timestamp = request.headers.get("svix-timestamp")
        svix_signature = request.headers.get("svix-signature")
        if not svix_id or not svix_timestamp or not svix_signature:
            raise HTTPException(status_code=400, detail="Missing headers")

        try:
            _verify_timestamp(svix_timestamp)
        except _WebhookVerificationError as e:
            raise HTTPException(status_code=400, detail=str(e))

        body = await request.body()

        try:
            return self.verify_signature(
                svix_id,
                svix_timestamp,
                body.decode(),
                signatures=svix_signature,
                model=returns,
            )
        except _WebhookVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")


def _default_webhook_verify():
    """Build a function that verifies the clerk webhook signature if the webhook secret
    is available. Otherwise return a function that raises an error.
    """
    if secret := os.environ.get("CLERK_WEBHOOKS_SECRET"):
        return _ClerkWebhookSigner(secret).verify_webhook

    async def _not_verify_webhook(request: Request, returns: type[_T]) -> _T:
        raise InternalError("Missing CLERK_WEBHOOKS_SECRET, clerk webhooks will raise an error")

    return _not_verify_webhook


_verify_webhook = _default_webhook_verify()


class Organization(BaseModel):
    object: Literal["organization"]
    slug: str | None = None
    id: str
    name: str | None = None


class User(BaseModel):
    object: Literal["user"]

    id: str


WebhookTypes = Literal["organization.updated", "organization.created", "organization.deleted"] | str


class Webhook(BaseModel):
    data: Annotated[Organization | User, Field(discriminator="object")]
    type: WebhookTypes


async def _clerk_organization_webhook(
    type: WebhookTypes,
    organization: Organization,
    system_storage: OrganizationSystemStorage,
):
    match type:
        case "organization.created":
            # Not actually creating the org record here
            # It will be done when authentication happens
            pass
        case "organization.updated":
            await system_storage.update_slug(
                org_id=organization.id,
                slug=organization.slug,
                display_name=organization.name,
            )
            # TODO: update slack channel name
        case "organization.deleted":
            await system_storage.delete_organization(organization.id)
        case _:
            pass


@router.post("")
async def clerk_webhook(
    request: Request,
    system_storage: OrgSystemStorageDep,
):
    webhook = await _verify_webhook(request, Webhook)

    match webhook.data:
        case Organization():
            await _clerk_organization_webhook(webhook.type, webhook.data, system_storage)
        case _:
            pass
    return Response(status_code=204)
