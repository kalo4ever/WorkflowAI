from unittest.mock import AsyncMock, patch

import pytest

from api.services.slack_notifications import (
    SlackNotificationDestination,
    _get_organization_str,  # pyright: ignore [reportPrivateUsage]
    _get_user_str,  # pyright: ignore [reportPrivateUsage]
    _should_send_slack_notification,  # pyright: ignore [reportPrivateUsage]
    get_user_and_org_str,
    send_slack_notification,
)
from core.domain.analytics_events.analytics_events import OrganizationProperties, UserProperties
from core.domain.events import Event


@pytest.mark.parametrize(
    "event, expected_output",
    [
        (Event(user_properties=UserProperties(user_email="test@example.com")), "test@example.com"),
        (Event(user_properties=UserProperties(user_email=None)), "An unknown user"),
        (Event(), "An unknown user"),
    ],
)
def test_get_user_str(event: Event, expected_output: str):
    assert _get_user_str(event) == expected_output


@pytest.mark.parametrize(
    "event, expected_output",
    [
        (
            Event(
                organization_properties=OrganizationProperties(tenant="some_id", organization_slug="test-org"),
            ),
            " (test-org)",
        ),
        (Event(organization_properties=OrganizationProperties(tenant="some_id", organization_slug=None)), ""),
        (Event(), ""),
    ],
)
def test_get_organization_str(event: Event, expected_output: str):
    assert _get_organization_str(event) == expected_output


@pytest.mark.parametrize(
    "event, expected_output",
    [
        (
            Event(
                user_properties=UserProperties(user_email="test@example.com"),
                organization_properties=OrganizationProperties(tenant="some_id", organization_slug="Test Org"),
            ),
            "test@example.com (Test Org)",
        ),
        (
            Event(
                user_properties=UserProperties(user_email="test@example.com"),
                organization_properties=OrganizationProperties(tenant="some_id", organization_slug=None),
            ),
            "test@example.com",
        ),
        (
            Event(
                user_properties=UserProperties(user_email=None),
                organization_properties=OrganizationProperties(tenant="some_id", organization_slug="Test Org"),
            ),
            "An unknown user (Test Org)",
        ),
        (Event(), "An unknown user"),
    ],
)
def test_get_user_and_org_str(event: Event, expected_output: str):
    assert get_user_and_org_str(event) == expected_output


@pytest.mark.parametrize(
    "env_name, user_email, should_send_slack_notification",
    [
        ("local", "email@example.com", True),
        ("staging", "email@example.com", True),
        ("prod", "email@example.com", True),
        ("prod", "justinthyme1612@gmail.com", False),
        ("prod", "jim@workflowai.com", False),
    ],
)
async def test_should_send_slack_notification(env_name: str, user_email: str, should_send_slack_notification: bool):
    with patch("os.environ.get") as mock_get_env:
        mock_get_env.return_value = env_name
        assert _should_send_slack_notification(user_email) == should_send_slack_notification


async def test_send_slack_notification_when_should_send():
    message = "Test message"
    user_email = "test@example.com"

    with (
        patch("api.services.slack_notifications._should_send_slack_notification") as mock_should_send,
        patch("api.services.slack_notifications.SlackClient") as mock_slack_client,
        patch("api.services.slack_notifications.logger") as mock_logger,
    ):
        mock_should_send.return_value = True
        mock_slack_client.return_value.send_message = AsyncMock()

        await send_slack_notification(message, user_email, destination=SlackNotificationDestination.CUSTOMER_JOURNEY)

        mock_should_send.assert_called_once_with(user_email=user_email)
        mock_slack_client.assert_called_once()
        mock_slack_client.return_value.send_message.assert_called_once_with(message)
        mock_logger.info.assert_not_called()


async def test_send_slack_notification_when_should_not_send():
    message = "Test message"
    user_email = "justinthyme1612@gmail.com"

    with (
        patch("api.services.slack_notifications._should_send_slack_notification") as mock_should_send,
        patch("api.services.slack_notifications.SlackClient") as mock_slack_client,
        patch("api.services.slack_notifications.logger") as mock_logger,
    ):
        mock_should_send.return_value = False
        mock_slack_client.return_value.send_message = AsyncMock()

        await send_slack_notification(message, user_email, destination=SlackNotificationDestination.CUSTOMER_JOURNEY)

        mock_should_send.assert_called_once_with(user_email=user_email)
        mock_slack_client.assert_not_called()
        mock_logger.info.assert_called_once_with(
            "Skipping Slack notification",
            extra={
                "slack_message": message,
                "user_email": user_email,
            },
        )
