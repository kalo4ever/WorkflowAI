import logging
from collections.abc import AsyncIterator
from typing import Any

from pydantic import ValidationError

from api.tasks.custom_tool.custom_tool_creation_agent import (
    CustomToolCreationAgentInput,
    stream_custom_tool_creation_agent,
)
from api.tasks.custom_tool.custom_tool_example_input_agent import (
    ToolInputExampleAgentInput,
    tool_input_example_agent,
)
from api.tasks.custom_tool.custom_tool_example_output_agent import (
    ToolOuptutExampleAgentInput,
    ToolOutputExampleAgentOutput,
    tool_output_example_agent,
)
from core.domain.fields.custom_tool_creation_chat_message import CustomToolCreationChatMessage

_logger = logging.getLogger(__name__)


class CustomToolService:
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    async def stream_creation_agent(
        cls,
        messages: list[CustomToolCreationChatMessage],
    ) -> AsyncIterator[CustomToolCreationChatMessage]:
        async for output in stream_custom_tool_creation_agent(
            CustomToolCreationAgentInput(
                messages=messages,
            ),
        ):
            if answer := output.answer:
                if type(answer) is dict:  # pyright: ignore[reportUnnecessaryComparison]
                    try:
                        # answer is sometimes returns as a dict, SDK bug ?
                        yield CustomToolCreationChatMessage.model_validate(answer)
                    except ValidationError as e:
                        _logger.error("Error validating ToolCreationChatMessage answer", exc_info=e)
                else:
                    yield answer

    @classmethod
    async def stream_example_input(
        cls,
        tool_name: str,
        tool_description: str,
        tool_schema: dict[str, Any],
    ) -> AsyncIterator[dict[str, Any]]:
        async for output in tool_input_example_agent(
            ToolInputExampleAgentInput(
                tool_name=tool_name,
                tool_description=tool_description,
                tool_schema=tool_schema,
            ),
        ):
            if output.example_tool_input:
                yield output.example_tool_input

    @classmethod
    async def stream_example_output(
        cls,
        tool_name: str,
        tool_description: str,
        tool_input: dict[str, Any] | None,
    ) -> AsyncIterator[ToolOutputExampleAgentOutput]:
        async for output in tool_output_example_agent(
            ToolOuptutExampleAgentInput(
                tool_name=tool_name,
                tool_description=tool_description,
                tool_input=tool_input,
            ),
        ):
            yield output
