import json

import pytest
from pytest_httpx import HTTPXMock

from core.storage.slack.webhook_client import SlackErrorSendingError, SlackWebhookClient


async def test_send_message(httpx_mock: HTTPXMock):
    # Test the send_message method of SlackClient
    webhook_url = "https://hooks.slack.com/services/test"
    message = "Test message"

    httpx_mock.add_response(status_code=200, text="ok")

    client = SlackWebhookClient(webhook_url)
    await client.send_message(message)

    request = httpx_mock.get_request()
    assert request is not None
    assert request.url == webhook_url
    assert json.loads(request.content) == {"text": "Test message"}


async def test_send_message_fail(httpx_mock: HTTPXMock):
    # Test the send_message method of SlackClient
    webhook_url = "https://hooks.slack.com/services/test"
    message = "Test message"

    httpx_mock.add_response(status_code=400, text="NOK")

    client = SlackWebhookClient(webhook_url)
    with pytest.raises(SlackErrorSendingError):
        await client.send_message(message)

    request = httpx_mock.get_request()
    assert request is not None
    assert request.url == webhook_url
    assert json.loads(request.content) == {"text": "Test message"}
