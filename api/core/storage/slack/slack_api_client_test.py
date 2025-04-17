import json
from typing import Any
from unittest.mock import patch

import pytest
from pytest_httpx import HTTPXMock

from core.domain.errors import InternalError
from core.storage.slack.slack_api_client import SlackApiClient
from tests.utils import fixtures_json


@pytest.fixture()
def slack_api_client():
    return SlackApiClient(bot_token="xoxb-1234567890")


class TestCheckResponse:
    @pytest.mark.parametrize(
        "parsed,expected_error",
        [
            ({"ok": False, "error": "channel_not_found"}, "channel_not_found"),
            ({"ok": False}, "Unknown error"),
        ],
    )
    async def test_check_response_error(
        self,
        slack_api_client: SlackApiClient,
        parsed: dict[str, Any],
        expected_error: str,
    ) -> None:
        # Using _ prefix since we're deliberately testing a protected method
        with patch("core.storage.slack.slack_api_client._logger") as mock_logger:
            with pytest.raises(InternalError):
                slack_api_client._check_response(parsed, "test operation")  # type: ignore[reportPrivateUsage]

            mock_logger.error.assert_called_once()

    async def test_check_response_success(self, slack_api_client: SlackApiClient) -> None:
        parsed: dict[str, Any] = {"ok": True}
        # Should not raise any exception
        slack_api_client._check_response(parsed, "test operation")  # type: ignore[reportPrivateUsage]


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
