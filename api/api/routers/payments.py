import logging
import os

import stripe
from fastapi import APIRouter
from pydantic import BaseModel, model_validator

from api.dependencies.security import RequiredUserOrganizationDep, UserDep
from api.dependencies.services import PaymentServiceDep
from api.dependencies.storage import OrganizationStorageDep
from api.services.payments import PaymentMethodResponse

router = APIRouter(prefix="/organization/payments")

_logger = logging.getLogger(__name__)

stripe.api_key = os.getenv("STRIPE_API_KEY")


class PaymentMethodRequest(BaseModel):
    payment_method_id: str
    payment_method_currency: str = "USD"


class PaymentMethodIdResponse(BaseModel):
    payment_method_id: str


@router.post("/payment-methods", description="Add a payment method to the organization")
async def add_payment_method(
    payment_service: PaymentServiceDep,
    request: PaymentMethodRequest,
    user_org: RequiredUserOrganizationDep,
) -> PaymentMethodIdResponse:
    return PaymentMethodIdResponse(
        payment_method_id=await payment_service.add_payment_method(user_org, request.payment_method_id),
    )


class CustomerCreatedResponse(BaseModel):
    customer_id: str


@router.post("/customers", description="Create a customer in Stripe for the organization")
async def create_customer(
    payment_service: PaymentServiceDep,
    userDep: UserDep,
) -> CustomerCreatedResponse:
    return CustomerCreatedResponse(customer_id=await payment_service.create_customer(userDep.sub if userDep else None))


class PaymentIntentCreatedResponse(BaseModel):
    client_secret: str
    payment_intent_id: str


class CreatePaymentIntentRequest(BaseModel):
    amount: float


@router.post("/payment-intents", description="Create a payment intent in Stripe for the organization")
async def create_payment_intent(
    request: CreatePaymentIntentRequest,
    payment_service: PaymentServiceDep,
    user_org: RequiredUserOrganizationDep,
) -> PaymentIntentCreatedResponse:
    payment_intent = await payment_service.create_payment_intent(user_org, request.amount, trigger="manual")
    if not payment_intent.client_secret:
        raise ValueError("Payment intent creation failed")
    return PaymentIntentCreatedResponse(
        client_secret=payment_intent.client_secret,
        payment_intent_id=payment_intent.id,
    )


@router.get("/payment-methods", description="Get the payment method attached to the organization")
async def get_payment_method(
    payment_service: PaymentServiceDep,
    user_org: RequiredUserOrganizationDep,
) -> PaymentMethodResponse | None:
    return await payment_service.get_payment_method(user_org)


@router.delete("/payment-methods", description="Delete the payment method attached to the organization")
async def delete_payment_method(
    payment_service: PaymentServiceDep,
    user_org: RequiredUserOrganizationDep,
) -> None:
    await payment_service.delete_payment_method(user_org)


class AutomaticPaymentRequest(BaseModel):
    opt_in: bool
    threshold: float | None = None
    balance_to_maintain: float | None = None

    @model_validator(mode="after")
    def validate_threshold_and_balance_to_maintain(self: "AutomaticPaymentRequest") -> "AutomaticPaymentRequest":
        if self.opt_in:
            if self.threshold is None or self.balance_to_maintain is None:
                raise ValueError("Threshold and balance_to_maintain are required when opt_in is true")
            if self.threshold > self.balance_to_maintain:
                raise ValueError("Threshold must be greater than balance_to_maintain")
        else:
            if self.threshold is not None or self.balance_to_maintain is not None:
                raise ValueError("Threshold and balance_to_maintain must be None when opt_in is false")
        return self


@router.put("/automatic-payments", description="Enable or disable automatic payments")
async def update_automatic_payments(
    request: AutomaticPaymentRequest,
    storage: OrganizationStorageDep,
) -> None:
    # Endpoint: PUT /organization/payments/automatic-payments
    # Body: { opt_in: bool, threshold: float, balance_to_maintain: float }
    # Response: 204 No Content

    await storage.update_automatic_payment(request.opt_in, request.threshold, request.balance_to_maintain)
