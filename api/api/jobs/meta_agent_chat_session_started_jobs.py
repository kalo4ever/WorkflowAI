from api.broker import broker
from api.jobs.common import MetaAgentServiceDep
from core.domain.events import MetaAgentChatSessionStartedEvent


@broker.task(retry_on_error=True, max_retries=1)
async def notify_meta_agent_chat_session_started(
    event: MetaAgentChatSessionStartedEvent,
    meta_agent_service: MetaAgentServiceDep,
):
    await meta_agent_service.notify_meta_agent_chat_session_started(event=event)


JOBS = [notify_meta_agent_chat_session_started]
