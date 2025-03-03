from unittest.mock import AsyncMock, Mock

import pytest
import stripe

from api.services.payments import PaymentMethodResponse, PaymentService
from core.domain.errors import BadRequestError
from core.domain.organization_settings import TenantData


@pytest.fixture()
def payment_service(mock_storage: Mock, mock_event_router: Mock, mock_analytics_service: Mock):
    return PaymentService(
        storage=mock_storage,
        event_router=mock_event_router,
        analytics_service=mock_analytics_service,
    )


class TestCreateCustomer:
    async def test_create_new_customer(
        self,
        payment_service: PaymentService,
        mock_storage: AsyncMock,
        monkeypatch: Mock,
    ):
        # Mock stripe.Customer.create
        mock_customer = Mock()
        mock_customer.id = "cus_123"
        mock_storage.organizations.get_organization.return_value = TenantData(
            tenant="test-tenant",
            name="Test Org",
            slug="test-org",
            stripe_customer_id=None,
        )
        mock_create = AsyncMock(return_value=mock_customer)
        monkeypatch.setattr(stripe.Customer, "create_async", mock_create)

        customer_id = await payment_service.create_customer("test@example.com")

        assert customer_id == "cus_123"
        mock_create.assert_called_once_with(
            name="Test Org",
            email="test@example.com",
            metadata={
                "organization_id": "",
                "tenant": "test-tenant",
                "slug": "test-org",
            },
        )
        mock_storage.organizations.update_customer_id.assert_called_once_with(stripe_customer_id="cus_123")

    async def test_return_existing_customer(
        self,
        payment_service: PaymentService,
        mock_storage: AsyncMock,
    ):
        # Set existing customer ID
        mock_storage.organizations.get_organization.return_value.stripe_customer_id = "existing_cus_123"

        customer_id = await payment_service.create_customer("test@example.com")

        assert customer_id == "existing_cus_123"
        mock_storage.organizations.update_customer_id.assert_not_called()


class TestAddPaymentMethod:
    async def test_add_payment_method(
        self,
        payment_service: PaymentService,
        mock_storage: AsyncMock,
        monkeypatch: Mock,
    ):
        mock_storage.organizations.get_organization.return_value.stripe_customer_id = "cus_123"

        # Mock stripe methods
        mock_payment_method = Mock()
        mock_payment_method.id = "pm_123"
        mock_attach = AsyncMock(return_value=mock_payment_method)
        mock_modify = AsyncMock()
        monkeypatch.setattr(stripe.PaymentMethod, "attach_async", mock_attach)
        monkeypatch.setattr(stripe.Customer, "modify_async", mock_modify)

        payment_method_id = await payment_service.add_payment_method(
            mock_storage.organizations.get_organization.return_value,
            "pm_123",
        )

        assert payment_method_id == "pm_123"
        mock_attach.assert_called_once_with(
            "pm_123",
            customer="cus_123",
        )
        mock_modify.assert_called_once_with(
            "cus_123",
            invoice_settings={"default_payment_method": "pm_123"},
        )

    async def test_add_payment_method_no_customer(
        self,
        payment_service: PaymentService,
        mock_storage: AsyncMock,
    ):
        mock_storage.organizations.get_organization.return_value.stripe_customer_id = None

        with pytest.raises(BadRequestError, match="Organization has no Stripe customer ID"):
            await payment_service.add_payment_method(
                mock_storage.organizations.get_organization.return_value,
                "pm_123",
            )

    async def test_add_payment_method_invalid_card(
        self,
        payment_service: PaymentService,
        mock_storage: AsyncMock,
        monkeypatch: Mock,
    ):
        mock_payment_method = Mock()
        mock_payment_method.id = "pm_123"
        mock_attach = AsyncMock(
            side_effect=stripe.CardError(
                message="Your card's security code is incorrect.",
                code="incorrect_cvc",
                param="cvc",
            ),
        )
        monkeypatch.setattr(stripe.PaymentMethod, "attach_async", mock_attach)

        with pytest.raises(stripe.CardError, match="Your card's security code is incorrect."):
            await payment_service.add_payment_method(
                mock_storage.organizations.get_organization.return_value,
                "pm_123",
            )


class TestGetPaymentMethod:
    async def test_get_payment_method(
        self,
        payment_service: PaymentService,
        mock_storage: AsyncMock,
        monkeypatch: Mock,
    ):
        mock_storage.organizations.get_organization.return_value.stripe_customer_id = "cus_123"

        # Mock stripe.Customer.retrieve
        mock_payment_method = Mock()
        mock_payment_method.id = "pm_123"
        mock_payment_method.card.last4 = "4242"
        mock_payment_method.card.brand = "visa"
        mock_payment_method.card.exp_month = 12
        mock_payment_method.card.exp_year = 2025

        mock_customer = Mock()
        mock_customer.invoice_settings.default_payment_method = mock_payment_method
        monkeypatch.setattr(stripe.Customer, "retrieve_async", AsyncMock(return_value=mock_customer))

        payment_method = await payment_service.get_payment_method(
            mock_storage.organizations.get_organization.return_value,
        )

        assert isinstance(payment_method, PaymentMethodResponse)
        assert payment_method.payment_method_id == "pm_123"
        assert payment_method.last4 == "4242"
        assert payment_method.brand == "visa"
        assert payment_method.exp_month == 12
        assert payment_method.exp_year == 2025

    async def test_get_payment_method_no_default(
        self,
        payment_service: PaymentService,
        mock_storage: AsyncMock,
        monkeypatch: Mock,
    ):
        mock_storage.organizations.get_organization.return_value.stripe_customer_id = "cus_123"

        mock_customer = Mock()
        mock_customer.invoice_settings.default_payment_method = None
        monkeypatch.setattr(stripe.Customer, "retrieve_async", AsyncMock(return_value=mock_customer))

        payment_method = await payment_service.get_payment_method(
            mock_storage.organizations.get_organization.return_value,
        )

        assert payment_method is None


class TestDeletePaymentMethod:
    async def test_delete_payment_method(
        self,
        payment_service: PaymentService,
        mock_storage: AsyncMock,
        monkeypatch: Mock,
    ):
        mock_storage.organizations.get_organization.return_value.stripe_customer_id = "cus_123"
        mock_storage.organizations.get_organization.return_value.automatic_payment_enabled = True
        mock_storage.organizations.get_organization.return_value.automatic_payment_threshold = 10.0
        mock_storage.organizations.get_organization.return_value.automatic_payment_balance_to_maintain = 15.0

        # Mock stripe.Customer.retrieve
        mock_payment_method = Mock()
        mock_payment_method.id = "pm_123"
        mock_payment_method.card.last4 = "4242"
        mock_payment_method.card.brand = "visa"
        mock_payment_method.card.exp_month = 12
        mock_payment_method.card.exp_year = 2025

        mock_customer = Mock()
        mock_customer.invoice_settings.default_payment_method = mock_payment_method
        monkeypatch.setattr(stripe.Customer, "retrieve_async", AsyncMock(return_value=mock_customer))

        monkeypatch.setattr(stripe.PaymentMethod, "detach_async", AsyncMock(return_value=mock_payment_method))
        mock_customer2 = Mock()
        mock_customer2.invoice_settings.default_payment_method = None
        monkeypatch.setattr(stripe.Customer, "modify_async", AsyncMock(return_value=mock_customer2))

        await payment_service.delete_payment_method(mock_storage.organizations.get_organization.return_value)

        mock_storage.organizations.update_automatic_payment.assert_called_once_with(
            opt_in=False,
            threshold=None,
            balance_to_maintain=None,
        )


class TestCreatePaymentIntent:
    async def test_create_payment_intent(
        self,
        payment_service: PaymentService,
        mock_storage: AsyncMock,
        monkeypatch: Mock,
    ):
        mock_storage.organizations.get_organization.return_value = TenantData(
            tenant="test-tenant",
            name="Test Org",
            slug="test-org",
            stripe_customer_id="cus_123",
        )

        # Mock customer retrieval
        mock_payment_method = Mock()
        mock_payment_method.id = "pm_123"
        mock_customer = Mock()
        mock_customer.invoice_settings.default_payment_method = mock_payment_method
        mock_customer_retrieve = AsyncMock(return_value=mock_customer)
        monkeypatch.setattr(stripe.Customer, "retrieve_async", mock_customer_retrieve)

        # Mock payment intent creation
        mock_payment_intent = Mock()
        mock_payment_intent.client_secret = "secret_123"
        mock_payment_intent.id = "pi_123"
        mock_payment_intent_create = AsyncMock(return_value=mock_payment_intent)
        monkeypatch.setattr(stripe.PaymentIntent, "create_async", mock_payment_intent_create)

        payment_intent = await payment_service.create_payment_intent(
            mock_storage.organizations.get_organization.return_value,
            100.0,
            trigger="manual",
        )

        assert payment_intent.client_secret == "secret_123"
        assert payment_intent.id == "pi_123"

        mock_payment_intent_create.assert_called_once_with(
            amount=10000,  # $100.00 in cents
            currency="usd",
            customer="cus_123",
            payment_method="pm_123",
            setup_future_usage="off_session",
            automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
            metadata={
                "organization_id": "",
                "tenant": "test-tenant",
                "slug": "test-org",
                "trigger": "manual",
            },
        )

    async def test_create_payment_intent_no_payment_method(
        self,
        payment_service: PaymentService,
        mock_storage: AsyncMock,
        monkeypatch: Mock,
    ):
        mock_storage.organizations.get_organization.return_value.stripe_customer_id = "cus_123"

        mock_customer = Mock()
        mock_customer.invoice_settings.default_payment_method = None
        monkeypatch.setattr(stripe.Customer, "retrieve_async", AsyncMock(return_value=mock_customer))

        with pytest.raises(ValueError, match="Organization has no default payment method"):
            await payment_service.create_payment_intent(
                mock_storage.organizations.get_organization.return_value,
                100.0,
                trigger="manual",
            )


class TestDecrementCredits:
    async def test_decrement_credits(
        self,
        payment_service: PaymentService,
        mock_storage: AsyncMock,
    ):
        # Mock the organization document returned after decrementing credits
        mock_org_doc = Mock()
        mock_org_doc.current_credits_usd = 10.0  # Above threshold
        mock_org_doc.locked_for_payment = False
        mock_org_doc.automatic_payment_enabled = False
        mock_org_doc.automatic_payment_threshold = None
        mock_org_doc.automatic_payment_balance_to_maintain = None
        mock_storage.organizations.decrement_credits.return_value = mock_org_doc

        await payment_service.decrement_credits("test-tenant", 100.0)

        mock_storage.organizations.decrement_credits.assert_called_once_with(tenant="test-tenant", credits=100.0)
        # No attempt to lock since credits are above threshold
        mock_storage.organizations.attempt_lock_for_payment.assert_not_called()

    async def test_decrement_credits_triggers_automatic_payment(
        self,
        payment_service: PaymentService,
        mock_storage: AsyncMock,
        monkeypatch: Mock,
    ):
        # Mock the organization document returned after decrementing credits
        org = TenantData(
            tenant="test-tenant",
            name="Test Org",
            slug="test-org",
            current_credits_usd=4.0,  # Below threshold
            automatic_payment_enabled=True,
            automatic_payment_threshold=5.0,
            automatic_payment_balance_to_maintain=10.0,
        )

        mock_storage.organizations.decrement_credits.return_value = org.model_copy()

        # Mock successful lock attempt
        mock_storage.organizations.attempt_lock_for_payment.return_value = org.model_copy(
            update={"locked_for_payment": True},
        )

        # Mock payment method retrieval
        mock_payment_method = Mock()
        mock_payment_method.payment_method_id = "pm_123"
        monkeypatch.setattr(
            payment_service,
            "get_payment_method",
            AsyncMock(return_value=mock_payment_method),
        )

        # Mock payment intent creation and confirmation
        mock_payment_intent = Mock()
        mock_payment_intent.id = "pi_123"
        mock_payment_intent.status = "succeeded"
        monkeypatch.setattr(
            payment_service,
            "create_payment_intent",
            AsyncMock(return_value=mock_payment_intent),
        )
        monkeypatch.setattr(
            stripe.PaymentIntent,
            "confirm_async",
            AsyncMock(return_value=mock_payment_intent),
        )

        await payment_service.decrement_credits("test-tenant", 3.0)

        # Verify all the expected calls
        mock_storage.organizations.decrement_credits.assert_called_once_with(tenant="test-tenant", credits=3.0)
        mock_storage.organizations.attempt_lock_for_payment.assert_called_once()
        mock_storage.organizations.unlock_for_payment.assert_called_once_with(is_failed=False)

    async def test_decrement_credits_automatic_payment_fails(
        self,
        payment_service: PaymentService,
        mock_storage: AsyncMock,
        monkeypatch: Mock,
    ):
        # Mock the organization document returned after decrementing credits
        mock_org_doc = Mock()
        mock_org_doc.current_credits_usd = 4.0  # Below threshold
        mock_org_doc.locked_for_payment = False
        mock_org_doc.automatic_payment_enabled = True  # Enable automatic payments
        mock_org_doc.automatic_payment_threshold = 5.0
        mock_org_doc.automatic_payment_balance_to_maintain = 10.0
        mock_storage.organizations.decrement_credits.return_value = mock_org_doc

        # Mock successful lock attempt
        mock_lock_doc = Mock()
        mock_lock_doc.locked_for_payment = True
        mock_storage.organizations.attempt_lock_for_payment.return_value = mock_lock_doc

        # Mock payment method retrieval
        mock_payment_method = Mock()
        mock_payment_method.payment_method_id = "pm_123"
        # Mock payment method retrieval to return None
        monkeypatch.setattr(
            payment_service,
            "get_payment_method",
            AsyncMock(return_value=None),
        )
        # Mock payment intent creation and confirmation
        mock_payment_intent = Mock()
        mock_payment_intent.id = "pi_123"
        monkeypatch.setattr(
            payment_service,
            "create_payment_intent",
            AsyncMock(return_value=mock_payment_intent),
        )

        await payment_service.decrement_credits("test-tenant", 100.0)

        # Verify all the expected calls
        mock_storage.organizations.decrement_credits.assert_called_once_with(tenant="test-tenant", credits=100.0)
        mock_storage.organizations.attempt_lock_for_payment.assert_called_once()
        mock_storage.organizations.unlock_for_payment.assert_called_once_with(is_failed=True)
