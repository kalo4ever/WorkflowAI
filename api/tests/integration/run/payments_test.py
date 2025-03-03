import asyncio
from typing import Any, Generator
from unittest.mock import AsyncMock, patch

import pytest
import stripe
from stripe._expandable_field import ExpandableField

from api.routers.stripe_webhooks import PaymentIntentData, StripeEvent, StripeEventData
from core.domain.models import Model
from tests.integration.common import (
    IntegrationTestClient,
    result_or_raise,
)


@pytest.fixture
def stripe_customer() -> stripe.Customer:
    customer = stripe.Customer(
        id="cus_123",
        object="customer",
        name="Test Org",
        email="test@example.com",
    )
    # Then update with invoice settings after payment method is attached
    customer.invoice_settings = stripe.Customer.InvoiceSettings(
        default_payment_method={
            "id": "pm_123",
            "object": "payment_method",
            "type": "card",
            "card": {"last4": "4242", "brand": "visa", "exp_month": 12, "exp_year": 2025},
        },
    )
    def_payment_meth: ExpandableField[stripe.PaymentMethod] = stripe.PaymentMethod(
        id="pm_123",
        object="payment_method",
        type="card",
    )

    customer.invoice_settings.default_payment_method = def_payment_meth
    customer.invoice_settings.default_payment_method.card = stripe.PaymentMethod.Card()
    customer.invoice_settings.default_payment_method.card.last4 = "4242"
    customer.invoice_settings.default_payment_method.card.brand = "visa"
    customer.invoice_settings.default_payment_method.card.exp_month = 12
    customer.invoice_settings.default_payment_method.card.exp_year = 2025
    return customer


@pytest.fixture
def stripe_payment_method() -> stripe.PaymentMethod:
    return stripe.PaymentMethod(
        id="pm_123",
        object="payment_method",
        type="card",
        card=stripe.Card(
            last4="4242",
            brand="visa",
            exp_month=12,
            exp_year=2025,
        ),
    )


@pytest.fixture
def stripe_payment_intent(test_client: IntegrationTestClient) -> stripe.PaymentIntent:
    payment_intent = stripe.PaymentIntent(
        id="pi_123",
        object="payment_intent",
        amount=500,  # $5.00
        status="requires_action",
        metadata={"tenant": test_client.tenant},
    )
    payment_intent.client_secret = "secret_123"
    return payment_intent


@pytest.fixture
def mocked_stripe(
    stripe_customer: stripe.Customer,
    stripe_payment_method: stripe.PaymentMethod,
    stripe_payment_intent: stripe.PaymentIntent,
) -> Generator[dict[str, Any], None, None]:
    with (
        patch("stripe.Customer", spec=stripe.Customer) as customer_cls,
        patch("stripe.PaymentMethod", spec=stripe.PaymentMethod) as payment_method_cls,
        patch("stripe.PaymentIntent", spec=stripe.PaymentIntent) as payment_intent_cls,
    ):
        # Setup async method returns
        customer_cls.create_async = AsyncMock(return_value=stripe_customer)
        customer_cls.modify_async = AsyncMock(return_value=stripe_customer)
        customer_cls.retrieve_async = AsyncMock(return_value=stripe_customer)

        payment_method_cls.attach_async = AsyncMock(return_value=stripe_payment_method)

        payment_intent_cls.create_async = AsyncMock(return_value=stripe_payment_intent)

        stripe_payment_intent_succeeded: stripe.PaymentIntent = stripe_payment_intent
        stripe_payment_intent_succeeded.status = "succeeded"
        payment_intent_cls.confirm_async = AsyncMock(
            return_value=stripe_payment_intent_succeeded,
        )

        yield {
            "customer": stripe_customer,
            "payment_method": stripe_payment_method,
            "payment_intent": stripe_payment_intent,
        }


@pytest.fixture
async def stripe_webhook_event(test_client: IntegrationTestClient) -> StripeEvent:
    return StripeEvent(
        id="evt_123",
        type="payment_intent.succeeded",
        data=StripeEventData(
            object=PaymentIntentData(
                object="payment_intent",
                id="pi_123",
                amount=500,
                metadata={"tenant": test_client.tenant},
                status="succeeded",
            ),
        ),
    )


async def test_decrement_credits(test_client: IntegrationTestClient):
    task = await test_client.create_task()

    # Check initial credits
    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))
    assert org["current_credits_usd"] == 10.0  # Initial credits
    assert org["automatic_payment_enabled"] is False

    # Mock a response that will consume all credits
    test_client.mock_openai_call(
        usage={
            "prompt_tokens": int(round(4 * 1 / 0.000_002_5)),  # prompt count for $8 on GPT_4O_2024_11_20
            "completion_tokens": 0,
        },
    )

    # First run should succeed but consume all credits
    await test_client.run_task_v1(task, model=Model.GPT_4O_2024_11_20)
    await test_client.wait_for_completed_tasks()

    # Verify credits are depleted
    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))
    assert org["automatic_payment_enabled"] is False
    await test_client.wait_for_completed_tasks()

    # Decrement credits
    test_client.mock_openai_call(
        usage={
            "prompt_tokens": int(round(4 * 1 / 0.000_002_5)),  # prompt count for $4 on GPT_4O_2024_11_20
            "completion_tokens": 0,
        },
    )

    # First run should succeed but consume all credits
    await test_client.run_task_v1(task, model=Model.GPT_4O_2024_11_20, use_cache="never")
    await test_client.wait_for_completed_tasks()

    # Verify credits are decremented
    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))
    assert org["automatic_payment_enabled"] is False

    # Nothing happens when we decrement credits when the automatic payment is disabled
    await test_client.run_task_v1(task, model=Model.GPT_4O_2024_11_20, use_cache="never")
    await test_client.wait_for_completed_tasks()

    # Verify credits are decremented
    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))
    assert org["current_credits_usd"] < 0
    assert org["automatic_payment_enabled"] is False


async def test_enable_automatic_payment(
    test_client: IntegrationTestClient,
    stripe_webhook_event: StripeEvent,
    mocked_stripe: dict[str, Any],
):
    task = await test_client.create_task()

    org = await test_client.get_org()
    assert org["current_credits_usd"] == pytest.approx(10)  # pyright: ignore reportUnknownArgumentType
    assert org["automatic_payment_enabled"] is False

    # Create customer
    await test_client.post("/_/organization/payments/customers")

    # Add payment method
    await test_client.post(
        "/_/organization/payments/payment-methods",
        json={"payment_method_id": "pm_123"},
    )

    # Enable automatic payments
    await test_client.put(
        "/_/organization/payments/automatic-payments",
        json={"opt_in": True, "threshold": 10, "balance_to_maintain": 10},
    )
    org = await test_client.get_org()
    assert org["current_credits_usd"] == pytest.approx(10)  # pyright: ignore reportUnknownArgumentType
    assert org["automatic_payment_enabled"] is True

    # Process webhook

    # Mock OpenAI call that will consume credits
    test_client.mock_openai_call(
        usage={
            "prompt_tokens": int(round(8 * 1 / 0.000_002_5)),
            "completion_tokens": 0,
        },
    )

    # Run task to trigger credit depletion
    await test_client.run_task_v1(task, model=Model.GPT_4O_2024_11_20, use_cache="never")

    await test_client.wait_for_completed_tasks()

    # Verify credits are decremented and not yet added because webhook is not yet mocked
    org = await test_client.get_org()
    assert org["current_credits_usd"] == pytest.approx(2)  # pyright: ignore reportUnknownArgumentType
    assert org["automatic_payment_enabled"] is True

    # Send webhook event
    with patch("stripe.Webhook.construct_event", return_value=stripe_webhook_event):
        await test_client.int_api_client.post(
            "/webhooks/stripe",
            headers={"Stripe-Signature": "mock_signature"},
            json={"some": "payload"},
        )

    # Verify credits are added
    org = await test_client.get_org()
    assert org["current_credits_usd"] == pytest.approx(7)  # pyright: ignore reportUnknownArgumentType
    assert org["automatic_payment_enabled"] is True


async def test_enable_automatic_payment_multiple_runs(
    test_client: IntegrationTestClient,
    stripe_webhook_event: StripeEvent,
    mocked_stripe: dict[str, Any],
):
    task = await test_client.create_task()

    # Check initial credits and automatic payment setting
    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))
    assert org["current_credits_usd"] == 10.0
    assert org["automatic_payment_enabled"] is False

    test_client.mock_openai_call(
        usage={
            "prompt_tokens": int(round(2 * 1 / 0.000_002_5)),
            "completion_tokens": 0,
        },
    )

    # Run task to trigger credit depletion
    await test_client.run_task_v1(task, model=Model.GPT_4O_2024_11_20, use_cache="never")
    await test_client.wait_for_completed_tasks()

    # Enable automatic payments
    result_or_raise(
        await test_client.int_api_client.put(
            "/_/organization/payments/automatic-payments",
            json={"opt_in": True, "threshold": 10, "balance_to_maintain": 10},
        ),
    )

    # Verify credits
    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))
    expected_credits = 8  # 10 - 2
    assert abs(org["current_credits_usd"] - expected_credits) < 0.001
    assert org["automatic_payment_enabled"] is True

    # Create customer and add payment method
    result_or_raise(await test_client.int_api_client.post("/_/organization/payments/customers"))
    result_or_raise(
        await test_client.int_api_client.post(
            "/_/organization/payments/payment-methods",
            json={"payment_method_id": "pm_123"},
        ),
    )

    # Process webhook

    async def send_webhook():
        with patch("stripe.Webhook.construct_event", return_value=stripe_webhook_event):
            await test_client.int_api_client.post(
                "/webhooks/stripe",
                headers={"Stripe-Signature": "mock_signature"},
                json={"some": "payload"},
            )

    # Run multiple tasks concurrently
    await asyncio.gather(
        test_client.run_task_v1(task, model=Model.GPT_4O_2024_11_20, use_cache="never"),
        send_webhook(),
        test_client.run_task_v1(task, model=Model.GPT_4O_2024_11_20, use_cache="never"),
        test_client.run_task_v1(task, model=Model.GPT_4O_2024_11_20, use_cache="never"),
    )
    await test_client.wait_for_completed_tasks()

    # not a full test, because the credits are added from webhook, but outlines the expected behavior
    # Verify final credits
    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))
    expected_credits = 7  # 10 - 6 + 5 (only once) - 2 (third run)
    assert abs(org["current_credits_usd"] - expected_credits) < 0.001
    assert org["automatic_payment_enabled"] is True


async def test_enable_automatic_payment_multiple_runs_with_failed_payment(
    test_client: IntegrationTestClient,
    mocked_stripe: dict[str, Any],
):
    task = await test_client.create_task()

    # Check initial credits
    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))
    assert org["current_credits_usd"] == 10.0
    assert org["automatic_payment_enabled"] is False

    test_client.mock_openai_call(
        usage={
            "prompt_tokens": int(round(5 * 1 / 0.000_002_5)),
            "completion_tokens": 0,
        },
    )

    # Run task to trigger credit depletion
    await test_client.run_task_v1(task, model=Model.GPT_4O_2024_11_20, use_cache="never")
    await test_client.wait_for_completed_tasks()

    # Enable automatic payments
    result_or_raise(
        await test_client.int_api_client.put(
            "/_/organization/payments/automatic-payments",
            json={"opt_in": True, "threshold": 5, "balance_to_maintain": 10},
        ),
    )
    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))
    assert org["current_credits_usd"] == 5.0
    assert org["automatic_payment_enabled"] is True
    assert org["automatic_payment_threshold"] == 5.0
    assert org["automatic_payment_balance_to_maintain"] == 10.0

    # Create customer and add payment method
    result_or_raise(await test_client.int_api_client.post("/_/organization/payments/customers"))
    result_or_raise(
        await test_client.int_api_client.post(
            "/_/organization/payments/payment-methods",
            json={"payment_method_id": "pm_123"},
        ),
    )

    # Override payment intent confirmation to simulate failure
    payment_intent = mocked_stripe["payment_intent"]
    payment_intent.status = "requires_action"

    # Run task to trigger failed payment
    await test_client.run_task_v1(task, model=Model.GPT_4O_2024_11_20, use_cache="never")
    await test_client.wait_for_completed_tasks()

    # Verify credits and payment failure
    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))
    expected_credits = 0  # 10 - 5 - 5
    assert abs(org["current_credits_usd"] - expected_credits) < 0.001
    assert org["automatic_payment_enabled"] is True
    assert org["last_payment_failed_at"] is not None


async def test_add_payment_method_invalid_card(
    test_client: IntegrationTestClient,
    mocked_stripe: dict[str, Any],
):
    # Create customer first
    result_or_raise(await test_client.int_api_client.post("/_/organization/payments/customers"))

    # Mock stripe.PaymentMethod.attach_async to raise a CardError
    with patch("stripe.PaymentMethod.attach_async") as mock_attach:
        mock_attach.side_effect = stripe.CardError(
            message="Your card's security code is incorrect.",
            param="cvc",
            code="incorrect_cvc",
            http_status=402,
            json_body={
                "error": {
                    "message": "Your card's security code is incorrect.",
                    "param": "cvc",
                    "code": "incorrect_cvc",
                },
            },
        )

        # Attempt to add invalid payment method
        response = await test_client.int_api_client.post(
            "/_/organization/payments/payment-methods",
            json={"payment_method_id": "pm_123"},
        )

        assert response.status_code == 402
        error_data = response.json()
        assert error_data["error"]["message"] == "Your card's security code is incorrect."
        assert error_data["error"]["code"] == "card_validation_error"

        # Verify the payment method was not attached
        mock_attach.assert_called_once()


async def test_enable_automatic_payment_multiple_runs_with_failed_payment_and_payment_method_added_after_failure(
    test_client: IntegrationTestClient,
    mocked_stripe: dict[str, Any],
):
    task = await test_client.create_task()

    # Check initial credits
    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))
    assert org["current_credits_usd"] == 10.0
    assert org["automatic_payment_enabled"] is False

    test_client.mock_openai_call(
        usage={
            "prompt_tokens": int(round(5 * 1 / 0.000_002_5)),
            "completion_tokens": 0,
        },
    )

    # Run task to trigger credit depletion
    await test_client.run_task_v1(task, model=Model.GPT_4O_2024_11_20, use_cache="never")
    await test_client.wait_for_completed_tasks()

    # Enable automatic payments
    result_or_raise(
        await test_client.int_api_client.put(
            "/_/organization/payments/automatic-payments",
            json={"opt_in": True, "threshold": 5, "balance_to_maintain": 10},
        ),
    )
    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))
    assert org["current_credits_usd"] == 5.0
    assert org["automatic_payment_enabled"] is True
    assert org["automatic_payment_threshold"] == 5.0
    assert org["automatic_payment_balance_to_maintain"] == 10.0

    # Create customer and add payment method
    result_or_raise(await test_client.int_api_client.post("/_/organization/payments/customers"))
    result_or_raise(
        await test_client.int_api_client.post(
            "/_/organization/payments/payment-methods",
            json={"payment_method_id": "pm_123"},
        ),
    )

    # Override payment intent confirmation to simulate failure
    payment_intent = mocked_stripe["payment_intent"]
    payment_intent.status = "requires_action"

    # Run task to trigger failed payment
    await test_client.run_task_v1(task, model=Model.GPT_4O_2024_11_20, use_cache="never")
    await test_client.wait_for_completed_tasks()

    # Verify credits and payment failure
    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))
    expected_credits = 0  # 10 - 5 - 5
    assert abs(org["current_credits_usd"] - expected_credits) < 0.001
    assert org["automatic_payment_enabled"] is True
    assert org["last_payment_failed_at"] is not None

    # Add payment method
    result_or_raise(
        await test_client.int_api_client.post(
            "/_/organization/payments/payment-methods",
            json={"payment_method_id": "pm_123"},
        ),
    )

    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))
    assert org["current_credits_usd"] == 0.0
    assert org["automatic_payment_enabled"] is True
    assert org["last_payment_failed_at"] is None
