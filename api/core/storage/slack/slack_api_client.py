import httpx

from core.storage.slack.slack_types import SlackMessage


class SlackApiClient:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token

    def _client(self):
        return httpx.AsyncClient(
            base_url="https://slack.com/api",
            headers={"Authorization": f"Bearer {self.bot_token}"},
        )

    async def create_channel(self, name: str) -> str:
        """Create a slack channel and return a channel id"""
        async with self._client() as client:
            response = await client.post(
                "/conversations.create",
                json={"name": name, "is_private": False},
            )
            response.raise_for_status()
            return response.json()["channel"]["id"]

    async def rename_channel(self, channel_id: str, name: str):
        """Rename a slack channel"""
        async with self._client() as client:
            await client.post(
                "/conversations.rename",
                json={"channel": channel_id, "name": name},
            )

    async def invite_users(self, channel_id: str, user_ids: list[str]):
        """Invite users to a slack channel"""
        async with self._client() as client:
            await client.post(
                "/conversations.invite",
                json={"channel": channel_id, "users": ",".join(user_ids)},
            )

    async def send_message(self, channel_id: str, message: SlackMessage):
        """Send a message to a slack channel"""
        async with self._client() as client:
            await client.post(
                "/chat.postMessage",
                json={"channel": channel_id, **message},
            )
