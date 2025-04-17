import json

import pytest
from pytest_httpx import HTTPXMock

from core.storage.slack.slack_api_client import SlackApiClient
from tests.utils import fixtures_json


@pytest.fixture()
def slack_api_client():
    return SlackApiClient(bot_token="xoxb-1234567890")


class TestCreateChannel:
    async def test_create_channel(self, slack_api_client: SlackApiClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://slack.com/api/conversations.create",
            json=fixtures_json("slack/channel.json"),
        )
        channel_id = await slack_api_client.create_channel("test-channel")
        assert channel_id == "C0EAQDV4Z"

        req = httpx_mock.get_request()
        assert req
        assert req.method == "POST"
        assert req.url == "https://slack.com/api/conversations.create"
        assert req.headers["Authorization"] == "Bearer xoxb-1234567890"
        assert json.loads(req.content) == {"name": "test-channel", "is_private": False}


class TestRenameChannel:
    async def test_rename_channel(self, slack_api_client: SlackApiClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://slack.com/api/conversations.rename",
            json=fixtures_json("slack/channel.json"),
        )
        await slack_api_client.rename_channel("C0EAQDV4Z", "test-channel")

        req = httpx_mock.get_request()
        assert req
        assert req.method == "POST"
        assert req.url == "https://slack.com/api/conversations.rename"
        assert json.loads(req.content) == {"channel": "C0EAQDV4Z", "name": "test-channel"}
