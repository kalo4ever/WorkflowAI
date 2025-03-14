import pytest

from core.domain.tool_call import ToolCallRequestWithID
from core.providers.google.google_provider_base import GoogleProviderBase
from core.providers.google.google_provider_domain import Candidate, CompletionResponse, Content, Part, UsageMetadata


@pytest.mark.parametrize(
    "instructions, expected",
    [
        (
            "You can use @browser-text to search, and external-tool to send an email to some email@example.com",
            "You can use browser-text to search, and external-tool to send an email to some email@example.com",
        ),
    ],
)
def test_sanitize_agent_instructions(instructions: str, expected: str) -> None:
    result = GoogleProviderBase.sanitize_agent_instructions(instructions)
    assert result == expected


def test_extract_native_tool_calls_empty_response() -> None:
    response = CompletionResponse(
        candidates=[
            Candidate(
                content=None,
            ),
        ],
        usageMetadata=UsageMetadata(),
    )
    result = GoogleProviderBase._extract_native_tool_calls(response)  # pyright: ignore[reportPrivateUsage]
    assert result == []


def test_extract_native_tool_calls_no_function_calls() -> None:
    response = CompletionResponse(
        candidates=[
            Candidate(
                content=Content(
                    role="model",
                    parts=[Part(text="some text")],
                ),
            ),
        ],
        usageMetadata=UsageMetadata(),
    )
    result = GoogleProviderBase._extract_native_tool_calls(response)  # pyright: ignore[reportPrivateUsage]
    assert result == []


def test_extract_native_tool_calls_with_function_calls() -> None:
    response = CompletionResponse(
        candidates=[
            Candidate(
                content=Content(
                    role="model",
                    parts=[
                        Part(
                            functionCall=Part.FunctionCall(
                                name="browser-text",
                                args={"url": "https://example.com"},
                            ),
                        ),
                        Part(
                            functionCall=Part.FunctionCall(
                                name="external-tool",
                                args={"param1": "value1"},
                            ),
                        ),
                    ],
                ),
            ),
        ],
        usageMetadata=UsageMetadata(),
    )
    result = GoogleProviderBase._extract_native_tool_calls(response)  # pyright: ignore[reportPrivateUsage]
    assert result == [
        ToolCallRequestWithID(
            tool_name="@browser-text",
            tool_input_dict={"url": "https://example.com"},
        ),
        ToolCallRequestWithID(
            tool_name="external-tool",
            tool_input_dict={"param1": "value1"},
        ),
    ]


def test_extract_native_tool_calls_missing_tool_name() -> None:
    response = CompletionResponse(
        candidates=[
            Candidate(
                content=Content(
                    role="model",
                    parts=[
                        Part(
                            functionCall=Part.FunctionCall(
                                name="non-existent-tool",
                                args={},
                            ),
                        ),
                    ],
                ),
            ),
        ],
        usageMetadata=UsageMetadata(),
    )
    result = GoogleProviderBase._extract_native_tool_calls(response)  # pyright: ignore[reportPrivateUsage]
    assert result == [
        ToolCallRequestWithID(
            tool_name="non-existent-tool",
            tool_input_dict={},
        ),
    ]
