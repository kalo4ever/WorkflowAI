from unittest.mock import patch

from api.jobs.task_schema_created_jobs import send_task_update_slack_notification
from core.domain.analytics_events.analytics_events import OrganizationProperties, UserProperties
from core.domain.events import TaskSchemaCreatedEvent
from core.storage.slack.webhook_client import SlackWebhookClient


@patch.dict(
    "os.environ",
    {
        "SLACK_WEBHOOK_URL_CUSTOMER_JOURNEY": "https://hooks.slack.com/services/test",
        "ENV_NAME": "local",
    },
)
async def test_send_task_update_slack_notification_new_task():
    with patch.object(SlackWebhookClient, "send_message") as mock_send_message:
        # Test for a new task creation
        event = TaskSchemaCreatedEvent(
            task_id="123",
            task_schema_id=1,
            skip_generation=False,
            user_properties=UserProperties(user_email="user@example.com"),
        )

        await send_task_update_slack_notification(event)

        mock_send_message.assert_called_once_with("user@example.com created a new task: 123")


@patch.dict(
    "os.environ",
    {
        "SLACK_WEBHOOK_URL_CUSTOMER_JOURNEY": "https://hooks.slack.com/services/test",
        "ENV_NAME": "local",
    },
    clear=True,
)
async def test_send_task_update_slack_notification_new_task_with_org():
    with patch.object(SlackWebhookClient, "send_message") as mock_send_message:
        # Test for a new task creation
        event = TaskSchemaCreatedEvent(
            task_id="123",
            task_schema_id=1,
            skip_generation=False,
            user_properties=UserProperties(user_email="user@example.com"),
            organization_properties=OrganizationProperties(
                tenant="org_uid1",
                organization_id="org_12345",
                organization_slug="some-org",
            ),
        )

        await send_task_update_slack_notification(event)

        mock_send_message.assert_called_once_with("user@example.com (some-org) created a new task: 123")


@patch.dict(
    "os.environ",
    {
        "SLACK_WEBHOOK_URL_CUSTOMER_JOURNEY": "https://hooks.slack.com/services/test",
        "WORKFLOWAI_APP_URL": "https://workflowai.com",
        "ENV_NAME": "local",
    },
)
async def test_send_task_update_slack_notification_new_task_with_org_and_domain():
    with patch.object(SlackWebhookClient, "send_message") as mock_send_message:
        # Test for a new task creation
        event = TaskSchemaCreatedEvent(
            task_id="some_task_id",
            task_schema_id=1,
            skip_generation=False,
            user_properties=UserProperties(user_email="user@example.com"),
            organization_properties=OrganizationProperties(
                tenant="org_uid2",
                organization_id="org_12345",
                organization_slug="some-org",
            ),
        )

        await send_task_update_slack_notification(event)

        mock_send_message.assert_called_once_with(
            "user@example.com (some-org) created a new task: <https://workflowai.com/some-org/agents/some_task_id/1|some_task_id>",
        )


@patch.dict(
    "os.environ",
    {
        "SLACK_WEBHOOK_URL_CUSTOMER_JOURNEY": "https://hooks.slack.com/services/test",
        "WORKFLOWAI_APP_URL": "https://workflowai.com",
        "ENV_NAME": "local",
    },
)
async def test_send_task_update_slack_notification_new_task_with_org_no_domain():
    with patch.object(SlackWebhookClient, "send_message") as mock_send_message:
        # Test for a new task creation
        event = TaskSchemaCreatedEvent(
            task_id="some_task_id",
            task_schema_id=1,
            skip_generation=False,
            user_properties=UserProperties(user_email="user@example.com"),
            organization_properties=OrganizationProperties(
                tenant="some-org.com",
                organization_id="some-org.com",
                organization_slug="some-org",
            ),
        )

        await send_task_update_slack_notification(event)

        mock_send_message.assert_called_once_with(
            "user@example.com (some-org) created a new task: <https://workflowai.com/some-org/agents/some_task_id/1|some_task_id>",
        )


@patch.dict(
    "os.environ",
    {
        "SLACK_WEBHOOK_URL_CUSTOMER_JOURNEY": "https://hooks.slack.com/services/test",
        "WORKFLOWAI_APP_URL": "https://workflowai.com",
        "ENV_NAME": "local",
    },
    clear=True,
)
async def test_send_task_update_slack_notification_new_task_with_org_no_slug():
    with patch.object(SlackWebhookClient, "send_message") as mock_send_message:
        # Test for a new task creation
        event = TaskSchemaCreatedEvent(
            task_id="some_task_id",
            task_schema_id=1,
            skip_generation=False,
            user_properties=UserProperties(user_email="user@example.com"),
            organization_properties=OrganizationProperties(
                tenant="some-org.com",
            ),
        )

        await send_task_update_slack_notification(event)

        mock_send_message.assert_called_once_with(
            "user@example.com created a new task: some_task_id",
        )


@patch.dict(
    "os.environ",
    {
        "SLACK_WEBHOOK_URL_CUSTOMER_JOURNEY": "https://hooks.slack.com/services/test",
        "ENV_NAME": "local",
    },
)
async def test_send_task_update_slack_notification_update_task():
    with patch.object(SlackWebhookClient, "send_message") as mock_send_message:
        # Test for a task update
        event = TaskSchemaCreatedEvent(
            task_id="456",
            task_schema_id=2,
            skip_generation=False,
            user_properties=UserProperties(user_email="user@example.com"),
        )

        await send_task_update_slack_notification(event)

        mock_send_message.assert_called_once_with("user@example.com updated a task schema: 456 (schema #2)")


@patch.dict(
    "os.environ",
    {
        "SLACK_WEBHOOK_URL_CUSTOMER_JOURNEY": "https://hooks.slack.com/services/test",
        "ENV_NAME": "local",
    },
)
async def test_send_task_update_slack_notification_unknown_user():
    with patch.object(SlackWebhookClient, "send_message") as mock_send_message:
        # Test for an unknown user
        event = TaskSchemaCreatedEvent(
            task_id="789",
            task_schema_id=3,
            skip_generation=False,
        )

        await send_task_update_slack_notification(event)

        mock_send_message.assert_called_once_with("An unknown user updated a task schema: 789 (schema #3)")
