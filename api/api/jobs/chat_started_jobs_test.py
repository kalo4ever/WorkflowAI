from unittest.mock import patch

import pytest

from api.jobs.chat_started_jobs import send_chat_started_slack_notification
from core.domain.analytics_events.analytics_events import OrganizationProperties, UserProperties
from core.domain.events import TaskChatStartedEvent
from core.storage.slack.client import SlackClient


@pytest.mark.parametrize(
    "event, expected_message",
    [
        (
            TaskChatStartedEvent(
                user_message="Hello, I want to create a task",
                user_properties=UserProperties(user_email="user@example.com"),
            ),
            'user@example.com started a chat to create a new task\nmessage: "Hello, I want to create a task"',
        ),
        (
            TaskChatStartedEvent(
                existing_task_name="ExistingTask",
                user_message="I want to update this task",
                user_properties=UserProperties(user_email="user@example.com"),
                organization_properties=OrganizationProperties(tenant="some_id", organization_slug="TestOrg"),
            ),
            'user@example.com (TestOrg) started a chat to update ExistingTask\nmessage: "I want to update this task"',
        ),
        (
            TaskChatStartedEvent(
                user_message="Creating a task without user info",
            ),
            'An unknown user started a chat to create a new task\nmessage: "Creating a task without user info"',
        ),
    ],
)
@patch.dict(
    "os.environ",
    {
        "SLACK_WEBHOOK_URL_CUSTOMER_JOURNEY": "https://hooks.slack.com/services/test",
        "ENV_NAME": "local",
    },
)
async def test_send_chat_started_slack_notification(event: TaskChatStartedEvent, expected_message: str):
    with patch.object(SlackClient, "send_message") as mock_send_message:
        await send_chat_started_slack_notification(event)
        mock_send_message.assert_called_once_with(expected_message)
