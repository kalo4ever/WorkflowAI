from api.broker import broker
from api.services.slack_notifications import SlackNotificationDestination, get_user_and_org_str, send_slack_notification
from core.domain.events import TaskChatStartedEvent


@broker.task(retry_on_error=True, max_retries=1)
async def send_chat_started_slack_notification(
    event: TaskChatStartedEvent,
):
    user_and_org_str = get_user_and_org_str(event=event)
    action_str = "update " + event.existing_task_name if event.existing_task_name else "create a new task"
    message = f'''{user_and_org_str} started a chat to {action_str}
message: "{event.user_message}"'''
    await send_slack_notification(
        message=message,
        user_email=event.user_properties.user_email if event.user_properties else None,
        destination=SlackNotificationDestination.CUSTOMER_JOURNEY,
    )


JOBS = [send_chat_started_slack_notification]
