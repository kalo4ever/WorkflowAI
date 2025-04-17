from api.broker import broker
from api.jobs.common import CustomerServiceDep
from core.domain.events import TaskChatStartedEvent


@broker.task(retry_on_error=True, max_retries=1)
async def send_chat_started_slack_notification(
    event: TaskChatStartedEvent,
    customer_service: CustomerServiceDep,
):
    await customer_service.send_chat_started(
        user=event.user_properties,
        existing_task_name=event.existing_task_name,
        user_message=event.user_message,
    )


JOBS = [send_chat_started_slack_notification]
