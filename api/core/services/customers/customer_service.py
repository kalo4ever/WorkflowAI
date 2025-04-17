import asyncio
import json
import logging
import os

from core.domain.analytics_events.analytics_events import UserProperties
from core.domain.errors import InternalError
from core.domain.events import (
    Event,
    FeaturesByDomainGenerationStarted,
    MetaAgentChatMessagesSent,
    TaskSchemaCreatedEvent,
)
from core.storage import ObjectNotFoundException
from core.storage.backend_storage import BackendStorage
from core.storage.slack.slack_api_client import SlackApiClient
from core.storage.slack.utils import get_slack_hyperlink

_logger = logging.getLogger(__name__)


class CustomerService:
    _SLEEP_BETWEEN_RETRIES = 0.1

    def __init__(self, storage: BackendStorage):
        self._storage = storage

    async def _get_or_create_slack_channel(self, clt: SlackApiClient, retries: int = 3):
        org = await self._storage.organizations.get_organization(include={"slack_channel_id", "slug", "uid"})
        if org.slack_channel_id:
            return org.slack_channel_id

        # Locking
        try:
            await self._storage.organizations.set_slack_channel_id("")
        except ObjectNotFoundException:
            # Slack channel already set so we can just try to get it again
            for _ in range(retries):
                await asyncio.sleep(self._SLEEP_BETWEEN_RETRIES)
                org = await self._storage.organizations.get_organization(include={"slack_channel_id", "slug"})
                if org.slack_channel_id:
                    return org.slack_channel_id

            raise InternalError("Failed to get or create slack channel", extra={"org_id": org.org_id, "slug": org.slug})

        channel_id = await clt.create_channel(f"customer-{org.slug}")
        await self._storage.organizations.set_slack_channel_id(channel_id)
        if invitees := os.environ.get("SLACK_BOT_INVITEES"):
            await clt.invite_users(channel_id, invitees.split(","))
        # TODO: trigger initial message and set channel description
        return channel_id

    async def _send_message(self, message: str):
        bot_token = os.environ.get("SLACK_BOT_TOKEN")
        if not bot_token:
            _logger.warning("SLACK_BOT_TOKEN is not set, skipping message sending")
            return

        clt = SlackApiClient(bot_token=bot_token)
        channel_id = await self._get_or_create_slack_channel(clt)

        await clt.send_message(channel_id, {"text": message})

    async def handle_customer_created(self):
        pass

    async def handle_customer_migrated(self, from_user_id: str | None, from_anon_id: str | None):
        # TODO: rename slack channel
        pass

    async def send_chat_started(self, user: UserProperties | None, existing_task_name: str | None, user_message: str):
        username = _readable_name(user)
        action_str = "update " + existing_task_name if existing_task_name else "create a new task"
        message = f'{username} started a chat to {action_str}\nmessage: "{user_message}"'

        await self._send_message(message)

    # TODO: avoid using event directly here
    async def send_task_update(self, event: TaskSchemaCreatedEvent):
        username = _readable_name(event.user_properties)
        task_str = _get_task_str_for_slack(event=event, task_id=event.task_id, task_schema_id=event.task_schema_id)

        if event.task_schema_id == 1:  # task creation
            message = f"{username} created a new task: {task_str}"
        else:  # task update
            message = f"{username} updated a task schema: {task_str} (schema #{event.task_schema_id})"

        await self._send_message(message)

    async def notify_features_by_domain_generation_started(self, event: FeaturesByDomainGenerationStarted):
        username = _readable_name(event.user_properties)
        message = f"{username} started to generate features for domain: {event.company_domain}"

        await self._send_message(message)

    async def notify_meta_agent_messages_sent(self, event: MetaAgentChatMessagesSent):
        username = _readable_name(event.user_properties)

        for message in event.messages:
            if message.role == "USER":
                message_str = f"{username} sent a message to the meta-agent:\n\n```{message.content}```"
            else:
                message_str = f"Meta-agent sent a message to {username}:\n\n```{message.content}```"

                if message.tool_call:
                    message_str += f"\n\n```Tool call: {json.dumps(message.tool_call.model_dump(), indent=2)}```"

            await self._send_message(message_str)


def _readable_name(user: UserProperties | None) -> str:
    if user:
        return user.user_email or "missing email"
    return "unknown user"


def _get_task_url(event: Event, task_id: str, task_schema_id: int) -> str | None:
    organization_slug = event.organization_properties.organization_slug if event.organization_properties else None
    if organization_slug is None:
        return None

    base_domain = os.environ.get("WORKFLOWAI_APP_URL")
    if base_domain is None:
        return None

    # Not super solid, will break if we change the task URL format in the web app, but we can't access the webapp URL schema from here.
    # Additionally, this code is purely for notification purposes, so it's not critical for the clients
    return f"{base_domain}/{organization_slug}/agents/{task_id}/{task_schema_id}"


def _get_task_str_for_slack(event: Event, task_id: str, task_schema_id: int) -> str:
    task_str = task_id
    task_url = _get_task_url(event=event, task_id=task_id, task_schema_id=task_schema_id)
    if task_url is not None:
        task_str = get_slack_hyperlink(url=task_url, text=task_str)
    return task_str
