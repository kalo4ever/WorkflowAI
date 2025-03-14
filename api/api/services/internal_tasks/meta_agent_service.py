import asyncio
import logging
from typing import AsyncIterator

from api.services.slack_notifications import SlackNotificationDestination, get_user_and_org_str, send_slack_notification
from api.services.tasks import list_agent_summaries
from api.tasks.extract_company_info_from_domain_task import safe_generate_company_description_from_email
from api.tasks.meta_agent import MetaAgentInput, meta_agent
from core.domain.events import EventRouter, MetaAgentChatMessagesSent, MetaAgentChatSessionStartedEvent
from core.domain.fields.chat_message import ChatMessage
from core.storage.backend_storage import BackendStorage
from core.utils.workflowai_documentation_utils import build_api_docs_prompt

FIRST_MESSAGE_CONTENT = (
    "Hey! I'm WorkflowAI's agent, you can ask me anything about the platform. How can I help you today?"
)


class MetaAgentService:
    def __init__(self, storage: BackendStorage, event_router: EventRouter):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.storage = storage
        self.event_router = event_router

    async def _build_meta_agent_input(
        self,
        user_email: str | None,
        messages: list[ChatMessage],
    ) -> MetaAgentInput:
        # Concurrently extract company info and list current agents
        company_description, current_agents = await asyncio.gather(
            safe_generate_company_description_from_email(
                user_email,
            ),
            list_agent_summaries(self.storage, limit=10),
        )
        current_agents = [str(agent) for agent in current_agents]

        return MetaAgentInput(
            messages=messages,
            company_context=MetaAgentInput.CompanyContext(
                company_name=company_description.company_name if company_description else None,
                company_description=company_description.description if company_description else None,
                company_locations=company_description.locations if company_description else None,
                company_industries=company_description.industries if company_description else None,
                company_products=company_description.products if company_description else None,
                current_agents=current_agents,
            ),
            workflowai_documentation=build_api_docs_prompt(),
        )

    def dispatch_new_user_messages_event(self, messages: list[ChatMessage]):
        # Extract the last message from the list since the latest "ASSISTANT" message
        latest_user_messages = [message for message in reversed(messages) if message.role == "USER"]
        if latest_user_messages:
            self.event_router(MetaAgentChatMessagesSent(messages=list(reversed(latest_user_messages))))
        else:
            self._logger.warning("No user message found in the list of messages")

    def dispatch_new_assistant_messages_event(self, messages: list[ChatMessage]):
        self.event_router(MetaAgentChatMessagesSent(messages=messages))

    async def stream_meta_agent_response(
        self,
        user_email: str | None,
        messages: list[ChatMessage],
    ) -> AsyncIterator[list[ChatMessage]]:
        if len(messages) == 0:
            self.event_router(MetaAgentChatSessionStartedEvent())
            yield [ChatMessage(role="ASSISTANT", content=FIRST_MESSAGE_CONTENT)]
            return

        self.dispatch_new_user_messages_event(messages)

        meta_agent_input = await self._build_meta_agent_input(user_email, messages)

        answer_messages: list[ChatMessage] = []
        async for chunk in meta_agent.stream(meta_agent_input):
            if chunk.output.messages:
                # role="ASSISTANT" is a protection against the LLM hallucinating and sending a "USER" message
                # never happened but who knows
                answer_messages = [
                    ChatMessage(role="ASSISTANT", content=message.content) for message in chunk.output.messages
                ]
                yield answer_messages

        self.dispatch_new_assistant_messages_event(answer_messages)

    async def notify_meta_agent_chat_session_started(self, event: MetaAgentChatSessionStartedEvent):
        user_and_org_str = get_user_and_org_str(event=event)

        message = f"{user_and_org_str} started a chat session with the meta-agent"

        await send_slack_notification(
            message=message,
            user_email=event.user_properties.user_email if event.user_properties else None,
            destination=SlackNotificationDestination.CUSTOMER_JOURNEY,
        )

    async def notify_meta_agent_messages_sent(self, event: MetaAgentChatMessagesSent):
        user_and_org_str = get_user_and_org_str(event=event)

        for message in event.messages:
            if message.role == "USER":
                message = f"{user_and_org_str} sent a message with the meta-agent:\n\n```{message.content}```"
            else:
                message = f"Meta-agent sent a message to {user_and_org_str}:\n\n```{message.content}```"

            await send_slack_notification(
                message=message,
                user_email=event.user_properties.user_email if event.user_properties else None,
                destination=SlackNotificationDestination.CUSTOMER_JOURNEY,
            )
