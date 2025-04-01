from collections.abc import AsyncIterator
from typing import Any

import workflowai
from pydantic import BaseModel, Field


class ToolInputExampleAgentInput(BaseModel):
    tool_name: str | None = Field(
        default=None,
        description="The name of the tool to generate an example input for",
    )
    tool_description: str | None = Field(
        default=None,
        description="The description of the tool to generate an example input for",
    )
    tool_schema: dict[str, Any] | None = Field(
        default=None,
        description="The JSON schema of the tool to generate an example input for",
    )


class ToolInputExampleAgentOutput(BaseModel):
    example_tool_input: dict[str, Any] | None = Field(
        default=None,
        description="The example input for the tool, enforcing the 'tool_schema'",
    )


INSTRUCTIONS = """You are a tool input generator specialized in creating realistic example inputs for tools based on their schema and description.

    Given a tool name, description, and its input schema, create a representative example input that demonstrates typical usage of the tool.

    The example must strictly follow the provided schema structure and data types.

    Choose realistic values that would make sense in the context of the tool's purpose.

    The example should be practical and illustrate common use cases for the tool."""


@workflowai.agent(
    id="tool-input-example",
    version=workflowai.VersionProperties(
        model=workflowai.Model.CLAUDE_3_7_SONNET_20250219,
        max_tokens=1000,
        instructions=INSTRUCTIONS,
    ),
)
def tool_input_example_agent(
    task_input: ToolInputExampleAgentInput,
) -> AsyncIterator[ToolInputExampleAgentOutput]: ...
