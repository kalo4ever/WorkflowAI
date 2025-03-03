import logging
import os
from typing import Literal

import stripe
from pydantic import BaseModel

from api.services.analytics import AnalyticsService
from core.domain.errors import BadRequestError
from core.domain.events import EventRouter
from core.domain.organization_settings import TenantData
from core.storage.backend_storage import BackendStorage
from core.utils.models.dumps import safe_dump_pydantic_model

_logger = logging.getLogger("PaymentService")

stripe.api_key = os.getenv("STRIPE_API_KEY")


class PaymentMethodResponse(BaseModel):
    payment_method_id: str
    last4: str
    brand: str
    exp_month: int
    exp_year: int


class PaymentService:
    def __init__(
        self,
        storage: BackendStorage,
        event_router: EventRouter,
        analytics_service: AnalyticsService,
    ):
        self._storage = storage.organizations
        self._task_run_storage = storage.task_runs
        self._event_router = event_router
        self._analytics_service = analytics_service

    def _get_stripe_customer_id_from_org(self, org_settings: TenantData) -> str:
        if org_settings.stripe_customer_id is None:
            raise BadRequestError(
                "Organization has no Stripe customer ID",
                capture=True,
                extra={"org_settings": safe_dump_pydantic_model(org_settings)},
            )
        return org_settings.stripe_customer_id

    async def add_payment_method(
        self,
        org_settings: TenantData,
        payment_method_id: str,
    ) -> str:
        stripe_customer_id = self._get_stripe_customer_id_from_org(org_settings)

        payment_method = await stripe.PaymentMethod.attach_async(
            payment_method_id,
            customer=stripe_customer_id,
        )

        # Clear the last payment failed at
        if org_settings.last_payment_failed_at is not None:
            await self._storage.unset_last_payment_failed_at()

        # Set as default payment method
        await stripe.Customer.modify_async(
            stripe_customer_id,
            invoice_settings={"default_payment_method": payment_method.id},
        )

        return payment_method.id

    async def create_customer(self, user_email: str | None) -> str:
        if not stripe.api_key:
            _logger.error("Stripe API key is not set. Skipping customer creation.")
            return ""

        org_settings = await self._storage.get_organization()
        if org_settings.stripe_customer_id is not None:
            return org_settings.stripe_customer_id

        customer = await stripe.Customer.create_async(
            name=org_settings.name or org_settings.slug,
            email=user_email if user_email is not None else f"abc@{org_settings.slug}.com",  # Cannot be null
            metadata={
                "organization_id": org_settings.org_id or "",
                "tenant": org_settings.tenant,
                "slug": org_settings.slug,
            },
        )

        await self._storage.update_customer_id(stripe_customer_id=customer.id)
        return customer.id

    async def create_payment_intent(
        self,
        org_settings: TenantData,
        amount: float,
        trigger: Literal["automatic", "manual"],
    ) -> stripe.PaymentIntent:
        stripe_customer_id = self._get_stripe_customer_id_from_org(org_settings)

        customer = await stripe.Customer.retrieve_async(
            stripe_customer_id,
            expand=["invoice_settings.default_payment_method"],
        )
        if customer.invoice_settings is None or customer.invoice_settings.default_payment_method is None:
            raise ValueError("Organization has no default payment method")

        payment_intent = await stripe.PaymentIntent.create_async(
            amount=int(amount * 100),
            currency="usd",
            customer=stripe_customer_id,
            payment_method=customer.invoice_settings.default_payment_method.id,  # pyright: ignore
            setup_future_usage="off_session",
            # For automatic payment processing, we need to disable redirects to avoid getting stuck in a redirect path.
            # This does not affect manual payment processing.
            automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
            metadata={
                "organization_id": org_settings.org_id or "",
                "tenant": org_settings.tenant,
                "slug": org_settings.slug,
                "trigger": trigger,
            },
        )

        if not payment_intent.client_secret:
            raise ValueError("Payment intent has no client secret")

        return payment_intent

    async def get_payment_method(self, org_settings: TenantData) -> PaymentMethodResponse | None:
        if not stripe.api_key:
            _logger.error("Stripe API key is not set. Skipping payment method retrieval.")
            return None

        stripe_customer_id = self._get_stripe_customer_id_from_org(org_settings)
        customer = await stripe.Customer.retrieve_async(
            stripe_customer_id,
            expand=["invoice_settings.default_payment_method"],
        )
        if customer.invoice_settings is None:
            raise ValueError("Organization has no invoice settings")

        if not customer.invoice_settings.default_payment_method:
            return None

        pm = customer.invoice_settings.default_payment_method
        return PaymentMethodResponse(
            payment_method_id=pm.id,  # pyright: ignore
            last4=pm.card.last4,  # pyright: ignore
            brand=pm.card.brand,  # pyright: ignore
            exp_month=pm.card.exp_month,  # pyright: ignore
            exp_year=pm.card.exp_year,  # pyright: ignore
        )

    async def delete_payment_method(self, org_settings: TenantData) -> None:
        stripe_customer_id = self._get_stripe_customer_id_from_org(org_settings)

        customer = await stripe.Customer.retrieve_async(stripe_customer_id)

        invoice_settings = customer.invoice_settings
        if invoice_settings is None:
            _logger.info("Organization has no invoice settings")
            return

        default_payment_method = invoice_settings.default_payment_method
        if default_payment_method is None:
            _logger.info("Organization has no default payment method")
            return

        await stripe.PaymentMethod.detach_async(
            default_payment_method,  # pyright: ignore
        )

        await stripe.Customer.modify_async(
            stripe_customer_id,
            invoice_settings={"default_payment_method": ""},
        )

        # Opt-out from automatic payments
        await self._storage.update_automatic_payment(opt_in=False, threshold=None, balance_to_maintain=None)

        _logger.info("Deleted payment method", extra={"payment_method_id": default_payment_method})  # pyright: ignore

        return

    @classmethod
    def _autocharge_amount(cls, tenant: TenantData):
        if (
            tenant.automatic_payment_threshold is None
            or tenant.automatic_payment_balance_to_maintain is None
            or tenant.current_credits_usd > tenant.automatic_payment_threshold
        ):
            return None

        amount = tenant.automatic_payment_balance_to_maintain - tenant.current_credits_usd
        # This can happen if automatic_payment_threshold > automatic_payment_balance_to_maintain
        # For example: threshold = 100, maintain = 50, current = 75
        # This would be a stupid case.
        if amount <= 0:
            _logger.warning(
                "Automatic payment would charge negative amount",
                extra={"tenant": tenant.model_dump(exclude_none=True, exclude={"providers"})},
            )
            # Returning the balance to maintain to avoid charging 0
            return tenant.automatic_payment_balance_to_maintain

        return amount

    async def _handle_payment_for_locked_org(self, org_settings: TenantData):
        charge_amount = self._autocharge_amount(org_settings)
        if charge_amount is None:
            # This should never happen
            _logger.error(
                "Charge amount is None. Discarding Automatic payment",
                extra={"org_settings": org_settings.model_dump()},
            )
            return False

        _logger.info(
            "Organization has less than threshold credits so automatic payment processing is starting",
            extra={"organization_settings": org_settings.model_dump()},
        )

        payment_intent = await self.create_payment_intent(org_settings, charge_amount, trigger="automatic")

        default_payment_method = await self.get_payment_method(org_settings)
        if default_payment_method is None:
            _logger.error("Organization has no default payment method")
            return False

        res = await stripe.PaymentIntent.confirm_async(
            payment_intent.id,
            payment_method=default_payment_method.payment_method_id,
        )
        _logger.info("Payment intent confirmed", extra={"res": res})
        return res.status == "succeeded"

    async def _check_and_process_automatic_payment(self):
        org_settings = await self._storage.attempt_lock_for_payment()
        if not org_settings:
            _logger.info("Failed to lock for payment")
            return

        try:
            success = await self._handle_payment_for_locked_org(org_settings)
        except Exception:
            success = False

        await self._storage.unlock_for_payment(is_failed=not success)

    async def decrement_credits(self, event_tenant: str, credits: float) -> None:
        org_doc = await self._storage.decrement_credits(tenant=event_tenant, credits=credits)

        if not org_doc.locked_for_payment and self._autocharge_amount(org_doc):
            # Not using the amount here, we will get the final amount post lock
            await self._check_and_process_automatic_payment()
