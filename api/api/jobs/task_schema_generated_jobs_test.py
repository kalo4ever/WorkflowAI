from unittest.mock import AsyncMock, patch

import pytest

from api.jobs.task_schema_generated_jobs import notify_slack_on_task_schema_generated
from api.tasks.chat_task_schema_generation.chat_task_schema_generation_task import AgentSchemaJson
from core.domain.analytics_events.analytics_events import UserProperties
from core.domain.events import TaskSchemaGeneratedEvent
from core.domain.fields.chat_message import ChatMessage
from core.domain.models import Model


async def test_notify_slack_on_task_schema_generated():
    event = TaskSchemaGeneratedEvent(
        updated_task_schema=AgentSchemaJson(agent_name="Test Task", input_json_schema={}, output_json_schema={}),
        version_identifier=Model.O1_MINI_2024_09_12.value,
        chat_messages=[ChatMessage(content="User request", role="USER")],
        assistant_answer="Assistant answer",
        previous_task_schema=None,
        user_properties=UserProperties(user_email="user@example.com"),  # Use UserProperties instance
    )
    with (
        patch(
            "api.jobs.task_schema_generated_jobs.slack_notifications.send_slack_notification",
        ) as mock_send_slack_notification,
    ):
        mock_send_slack_notification.return_value = AsyncMock()

        await notify_slack_on_task_schema_generated(event)

        # Expected to send notifications for the original model and the candidate models
        total_notifications = 1
        assert mock_send_slack_notification.await_count == total_notifications


@pytest.mark.parametrize("env_var_value", ["true", "True"])
async def test_notify_slack_on_task_schema_generated_is_skipped_when_needed(env_var_value: str):
    event = TaskSchemaGeneratedEvent(
        updated_task_schema=AgentSchemaJson(agent_name="Test Task", input_json_schema={}, output_json_schema={}),
        version_identifier=Model.O1_MINI_2024_09_12.value,
        chat_messages=[ChatMessage(content="User request", role="USER")],
        assistant_answer="Assistant answer",
        previous_task_schema=None,
        user_properties=UserProperties(user_email="user@example.com"),  # Use UserProperties instance
    )
    with (
        patch(
            "api.jobs.task_schema_generated_jobs.slack_notifications.send_slack_notification",
        ) as mock_send_slack_notification,
        patch("os.getenv", return_value=env_var_value) as mock_getenv,
    ):
        mock_getenv.return_value = env_var_value
        mock_send_slack_notification.return_value = AsyncMock()

        await notify_slack_on_task_schema_generated(event)

        # Expected to send notifications for the original model and the candidate models
        total_notifications = 0
        assert mock_send_slack_notification.await_count == total_notifications
