from api.broker import broker
from api.jobs.common import CustomerServiceDep
from core.domain.events import MetaAgentChatMessagesSent


@broker.task(retry_on_error=True, max_retries=1)
async def notify_meta_agent_chat_messages_sent(
    event: MetaAgentChatMessagesSent,
    customer_service: CustomerServiceDep,
):
    await customer_service.notify_meta_agent_messages_sent(event=event)


JOBS = [notify_meta_agent_chat_messages_sent]
