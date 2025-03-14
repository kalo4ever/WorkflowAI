from typing import Any, Optional, cast

from pydantic import BaseModel

from core.domain.llm_usage import LLMUsage
from core.domain.message import Message
from core.domain.models import Provider
from core.domain.tool_call import ToolCallRequestWithID
from core.providers.base.models import StandardMessage


class LLMCompletion(BaseModel):
    duration_seconds: float | None = None

    messages: list[dict[str, Any]]
    response: Optional[str] = None

    tool_calls: list[ToolCallRequestWithID] | None = None

    usage: LLMUsage

    # The provider that was used to generate the completion
    provider: Provider

    def incur_cost(self) -> bool:
        return not (self.response is None and self.usage.completion_token_count == 0)

    def to_messages(self) -> list[Message]:
        # Convert the LLMCompletion to a list of messages
        # Warning: this will only work if the LLMCompletion messages has been converted to
        # a list of standard messages
        base = [Message.from_standard(cast(StandardMessage, message)) for message in self.messages]

        if self.tool_calls or self.response:
            base.append(
                Message(content=self.response or "", tool_call_requests=self.tool_calls, role=Message.Role.ASSISTANT),
            )
        return base


def total_tokens_count(completions: list[LLMCompletion] | None) -> tuple[float | None, float | None]:
    """Returns the total number of input / completion tokens used in the task run"""
    if not completions:
        return (None, None)

    input_tokens: float | None = None
    output_tokens: float | None = None
    for completion in completions:
        if not completion.usage:
            continue
        if completion.usage.prompt_token_count is not None:
            input_tokens = (input_tokens or 0) + completion.usage.prompt_token_count
        if completion.usage.completion_token_count is not None:
            output_tokens = (output_tokens or 0) + completion.usage.completion_token_count

    return (input_tokens, output_tokens)
