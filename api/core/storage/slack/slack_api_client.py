import logging
from typing import Any, Optional

import httpx
from pydantic import BaseModel

from core.domain.errors import InternalError
from core.storage.slack.slack_types import SlackMessage

_logger = logging.getLogger(__name__)


class SlackApiClient:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token

    def _client(self):
        return httpx.AsyncClient(
            base_url="https://slack.com/api",
            headers={"Authorization": f"Bearer {self.bot_token}", "Content-Type": "application/json; charset=utf-8"},
        )

    def _check_response(
        self,
        parsed: dict[str, Any],
        operation_name: str,
    ) -> None:
        """Check if Slack API response has ok=True, log and possibly raise error if not"""
        if not parsed.get("ok", False):
            error_msg = f"Slack client failed to {operation_name}"
            error = parsed.get("error", "Unknown error")

            _logger.error(error_msg, extra={"error_msg": error})
            raise InternalError(error_msg, extra={"error": error})

    async def post(
        self,
        endpoint: str,
        json_data: dict[str, Any],
        operation_name: str,
        error_context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make a POST request to Slack API and check response"""
        async with self._client() as client:
            response = await client.post(endpoint, json=json_data)
            parsed = response.json()

            self._check_response(
                parsed,
                operation_name,
            )

            response.raise_for_status()
            return parsed

    async def get(
        self,
        endpoint: str,
        params: dict[str, str],
        operation_name: str,
        error_context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make a GET request to Slack API and check response"""
        async with self._client() as client:
            response = await client.get(endpoint, params=params)
            parsed = response.json()

            self._check_response(
                parsed,
                operation_name,
            )

            response.raise_for_status()
            return parsed

    async def create_channel(self, name: str) -> str:
        """Create a slack channel and return a channel id"""
        parsed = await self.post(
            "/conversations.create",
            json_data={"name": name, "is_private": False},
            operation_name="create slack channel",
            error_context={"name": name},
        )
        return parsed["channel"]["id"]

    async def rename_channel(self, channel_id: str, name: str):
        """Rename a slack channel"""
        await self.post(
            "/conversations.rename",
            json_data={"channel": channel_id, "name": name},
            operation_name="rename slack channel",
            error_context={"channel_id": channel_id, "name": name},
        )

    async def invite_users(self, channel_id: str, user_ids: list[str]):
        """Invite users to a slack channel"""
        await self.post(
            "/conversations.invite",
            json_data={"channel": channel_id, "users": ",".join(user_ids)},
            operation_name="invite users to slack channel",
            error_context={"channel_id": channel_id, "user_ids": user_ids},
        )

    async def send_message(self, channel_id: str, message: SlackMessage) -> dict[str, Any]:
        """Send a message to a slack channel"""
        return await self.post(
            "/chat.postMessage",
            json_data={"channel": channel_id, **message},
            operation_name="send slack message",
            error_context={"channel_id": channel_id},
        )

    # TODO: not user yet, we need to add 'pins:write' scope to the bot token
    async def send_pinned_message(self, channel_id: str, message: SlackMessage):
        """Send a message to a slack channel and pin it"""
        message_payload = await self.send_message(channel_id, message)
        await self.post(
            "/pins.add",
            json_data={"channel": channel_id, "timestamp": message_payload["ts"]},
            operation_name="pin slack message",
            error_context={"channel_id": channel_id, "message": message},
        )

    async def set_channel_topic(self, channel_id: str, topic: str):
        """Set the topic of a slack channel"""
        await self.post(
            "/conversations.setTopic",
            json_data={"channel": channel_id, "topic": topic},
            operation_name="set slack channel topic",
            error_context={"channel_id": channel_id, "topic": topic},
        )

    async def set_channel_purpose(self, channel_id: str, purpose: str):
        """Set the purpose of a slack channel"""
        await self.post(
            "/conversations.setPurpose",
            json_data={"channel": channel_id, "purpose": purpose},
            operation_name="set slack channel purpose",
            error_context={"channel_id": channel_id, "purpose": purpose},
        )

    class ChannelInfo(BaseModel):
        name: str

        class Topic(BaseModel):
            value: str

        topic: Topic

    async def get_channel_info(self, channel_id: str):
        parsed = await self.get(
            "/conversations.info",
            params={"channel": channel_id},
            operation_name="get slack channel info",
            error_context={"channel_id": channel_id},
        )
        return self.ChannelInfo.model_validate(parsed["channel"])
