from typing import Any

from core.domain.llm_completion import LLMCompletion
from core.domain.llm_usage import LLMUsage
from core.domain.message import Message
from core.domain.models import Provider
from core.domain.tool_call import ToolCallRequestWithID
from core.providers.base.models import StandardMessage


def _llm_completion(
    messages: list[dict[str, Any]],
    usage: LLMUsage,
    response: str | None = None,
    tool_calls: list[ToolCallRequestWithID] | None = None,
):
    return LLMCompletion(
        messages=messages,
        usage=usage,
        response=response,
        tool_calls=tool_calls,
        provider=Provider.OPEN_AI,
    )


class TestLLMCompletionToMessages:
    def test_to_messages_with_response(self):
        completion = _llm_completion(
            messages=[{"role": "user", "content": "Hello world"}],
            response="Hello back!",
            usage=LLMUsage(),
        )

        messages = completion.to_messages()
        assert len(messages) == 2
        assert messages[0].role == Message.Role.USER
        assert messages[0].content == "Hello world"
        assert messages[1].role == Message.Role.ASSISTANT
        assert messages[1].content == "Hello back!"

    def test_to_messages_without_response(self):
        completion = _llm_completion(
            messages=[{"role": "system", "content": "System prompt"}, {"role": "user", "content": "User message"}],
            response=None,
            usage=LLMUsage(),
        )

        messages = completion.to_messages()
        assert len(messages) == 2
        assert messages[0].role == Message.Role.SYSTEM
        assert messages[0].content == "System prompt"
        assert messages[1].role == Message.Role.USER
        assert messages[1].content == "User message"

    def test_to_messages_with_complex_content(self):
        standard_msg: StandardMessage = {
            "role": "user",
            "content": [
                {"type": "text", "text": "First line"},
                {"type": "text", "text": "Second line"},
                {
                    "type": "image_url",
                    "image_url": {"url": "http://example.com/image.jpg"},
                },
            ],
        }

        completion = LLMCompletion(
            messages=[standard_msg],  # pyright: ignore [reportArgumentType]
            response="Got your message with image",
            usage=LLMUsage(),
            provider=Provider.OPEN_AI,
        )

        messages = completion.to_messages()
        assert len(messages) == 2
        assert messages[0].role == Message.Role.USER
        assert messages[0].content == "First line\nSecond line"
        assert messages[0].files is not None
        assert len(messages[0].files) == 1
        assert messages[0].files[0].url == "http://example.com/image.jpg"
        assert messages[1].role == Message.Role.ASSISTANT
        assert messages[1].content == "Got your message with image"

    def test_with_tool_calls_and_response(self):
        completion = _llm_completion(
            messages=[{"role": "user", "content": "Hello world"}],
            response="Hello back!",
            usage=LLMUsage(),
            tool_calls=[ToolCallRequestWithID(id="1", tool_name="test_tool", tool_input_dict={"arg1": "value1"})],
        )

        messages = completion.to_messages()
        assert messages == [
            Message(content="Hello world", role=Message.Role.USER),
            Message(
                content="Hello back!",
                role=Message.Role.ASSISTANT,
                tool_call_requests=[
                    ToolCallRequestWithID(id="1", tool_name="test_tool", tool_input_dict={"arg1": "value1"}),
                ],
            ),
        ]
