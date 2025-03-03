import logging
import os
from typing import Literal

import stripe
from fastapi import APIRouter, Header, Request, Response
from pydantic import BaseModel

from api.dependencies.security import SystemStorageDep
from core.domain.errors import DefaultError

router = APIRouter(prefix="/webhooks/stripe", include_in_schema=False)
_logger = logging.getLogger(__name__)


class PaymentIntentData(BaseModel):
    object: Literal["payment_intent"]
    id: str
    amount: int
    metadata: dict[str, str]
    status: str


class StripeEventData(BaseModel):
    object: PaymentIntentData


class StripeEvent(BaseModel):
    id: str
    type: Literal[
        "charge.succeeded",
        "payment_intent.succeeded",
        "payment_intent.requires_action",
        "payment_intent.requires_payment_method",
    ]
    data: StripeEventData


async def verify_stripe_signature(
    request: Request,
    stripe_signature: str | None = Header(None, alias="Stripe-Signature"),
) -> stripe.Event:
    if not stripe_signature:
        raise DefaultError(
            "No signature header",
            capture=True,
            status_code=400,
        )

    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        raise DefaultError(
            "Webhook secret not configured",
            capture=True,
            status_code=500,
        )

    body = await request.body()
    stripe_event: stripe.Event = stripe.Webhook.construct_event(  # type: ignore
        payload=body,
        sig_header=str(stripe_signature),
        secret=str(webhook_secret),
    )
    _logger.info("Raw Stripe Event", extra={"stripe_event": stripe_event})
    return stripe_event


@router.post("")
async def stripe_webhook(
    storage: SystemStorageDep,
    request: Request,
    stripe_signature: str | None = Header(None, alias="Stripe-Signature"),
) -> Response:
    _logger.debug("Received Stripe webhook", extra={"request": request, "stripe_signature": stripe_signature})
    event = await verify_stripe_signature(request, stripe_signature)

    match event.type:
        case "charge.succeeded":
            _logger.info("Charge succeeded", extra={"event": event.data.object})
        case "payment_intent.succeeded":
            validated_event = StripeEvent.model_validate(event)
            payment_intent = validated_event.data.object
            metadata = payment_intent.metadata
            tenant = metadata.get("tenant")

            amount_usd = payment_intent.amount / 100
            if not tenant:
                raise DefaultError(
                    capture=True,
                    status_code=400,
                    detail="No tenant in payment intent metadata",
                )
            await storage.add_credits_to_tenant(tenant, amount_usd)
            _logger.info("Added credits to organization", extra={"tenant": tenant, "amount_usd": amount_usd})

        case "payment_intent.requires_action":
            _logger.info("Payment requires action", extra={"event": event.data.object})

        case "payment_intent.payment_failed":
            _logger.info("Payment failed", extra={"event": event.data.object})
        case _:
            _logger.info("Unhandled Stripe event", extra={"event": event.data.object})

    return Response(status_code=200)
