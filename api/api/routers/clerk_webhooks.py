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
from core.storage.organization_storage import OrganizationSystemStorage

router = APIRouter(prefix="/webhooks/clerk", include_in_schema=False)
_logger = logging.getLogger(__name__)


def _decoded_secret(raw: str):
    signer = raw.split("_")[1]
    if not signer:
        raise ValueError("Missing CLERK_WEBHOOK_SECRET")
    return base64.b64decode(signer)


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


_clerk_webhook_secret = _decoded_secret(os.environ["CLERK_WEBHOOKS_SECRET"])


_T = TypeVar("_T", bound=BaseModel)


def _compute_signature(id: str, timestamp: str, body: str, secret: bytes):
    signedContent = f"{id}.{timestamp}.{body}".encode()
    return hmac.new(secret, signedContent, hashlib.sha256).digest()


def _verify_signature(id: str, timestamp: str, body: str, secret: bytes, signatures: str, model: type[_T]) -> _T:
    signed_bytes = _compute_signature(id, timestamp, body, secret)

    for versioned in signatures.split(" "):
        (version, signature) = versioned.split(",")
        if version != "v1":
            continue
        sig_bytes = base64.b64decode(signature)
        if hmac.compare_digest(signed_bytes, sig_bytes):
            return model.model_validate_json(body)
    raise _WebhookVerificationError("Invalid signature")


async def _verify_webhook(request: Request, returns: type[_T]) -> _T:
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
        return _verify_signature(
            svix_id,
            svix_timestamp,
            body.decode(),
            secret=_clerk_webhook_secret,
            signatures=svix_signature,
            model=returns,
        )
    except _WebhookVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")


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
