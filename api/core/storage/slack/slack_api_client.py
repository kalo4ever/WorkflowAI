import httpx
from pydantic import BaseModel

from core.domain.errors import InternalError
from core.storage.slack.slack_types import SlackMessage


class SlackApiClient:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token

    def _client(self):
        return httpx.AsyncClient(
            base_url="https://slack.com/api",
            headers={"Authorization": f"Bearer {self.bot_token}", "Content-Type": "application/json; charset=utf-8"},
        )

    async def create_channel(self, name: str) -> str:
        """Create a slack channel and return a channel id"""
        async with self._client() as client:
            response = await client.post(
                "/conversations.create",
                json={"name": name, "is_private": False},
            )
            response.raise_for_status()
            parsed = response.json()
            if not parsed["ok"]:
                raise InternalError("Failed to create slack channel", extra={"name": name, "error": parsed["error"]})
            return response.json()["channel"]["id"]

    async def rename_channel(self, channel_id: str, name: str):
        """Rename a slack channel"""
        async with self._client() as client:
            res = await client.post(
                "/conversations.rename",
                json={"channel": channel_id, "name": name},
            )
            res.raise_for_status()

    async def invite_users(self, channel_id: str, user_ids: list[str]):
        """Invite users to a slack channel"""
        async with self._client() as client:
            res = await client.post(
                "/conversations.invite",
                json={"channel": channel_id, "users": ",".join(user_ids)},
            )
            res.raise_for_status()

    async def send_message(self, channel_id: str, message: SlackMessage):
        """Send a message to a slack channel"""
        async with self._client() as client:
            res = await client.post(
                "/chat.postMessage",
                json={"channel": channel_id, **message},
            )
            res.raise_for_status()

    async def set_channel_topic(self, channel_id: str, topic: str):
        """Set the topic of a slack channel"""
        async with self._client() as client:
            res = await client.post(
                "/conversations.setTopic",
                json={"channel": channel_id, "topic": topic},
            )
            res.raise_for_status()

    async def set_channel_purpose(self, channel_id: str, purpose: str):
        """Set the purpose of a slack channel"""
        async with self._client() as client:
            res = await client.post(
                "/conversations.setPurpose",
                json={"channel": channel_id, "purpose": purpose},
            )
            res.raise_for_status()

    class ChannelInfo(BaseModel):
        name: str

        class Topic(BaseModel):
            value: str

        topic: Topic

    async def get_channel_info(self, channel_id: str):
        async with self._client() as client:
            response = await client.get(
                "/conversations.info",
                params={"channel": channel_id},
            )
            response.raise_for_status()
            parsed = response.json()
            if not parsed["ok"]:
                raise InternalError(
                    "Failed to get slack channel info",
                    extra={"channel_id": channel_id, "error": parsed["error"]},
                )
            return self.ChannelInfo.model_validate(parsed["channel"])
