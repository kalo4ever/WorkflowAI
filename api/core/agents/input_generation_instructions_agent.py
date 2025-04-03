from typing import Any

import workflowai
from pydantic import BaseModel, Field

from core.domain.fields.chat_message import ChatMessage


class InputGenerationInstructionsInput(BaseModel):
    creation_chat_messages: list[ChatMessage] | None = Field(
        default=None,
        description="The chat messages that originated the creation of the agent",
    )
    agent_name: str | None = Field(default=None, description="The name of the agent that the input belongs to")
    input_json_schema: dict[str, Any] | None = Field(
        default=None,
        description="The JSON schema for the input of the agent",
    )
    output_json_schema: dict[str, Any] | None = Field(
        default=None,
        description="The JSON schema for the output of the agent",
    )


class InputGenerationInstructionsOutput(BaseModel):
    input_generation_instructions: str | None = Field(
        default=None,
        description="The instructions for generating an example input for the agent",
    )


INSTRUCTIONS = """You are an instruction generation specialist focused on creating clear guidelines for input data generation that will be passed to another agent, the Input Generation Agent.

    Focus solely on extracting relevant information from the 'creation_chat_messages' (e.g., URLs to use), as the Input Generation Agent also has access to the agent_name and the input/output schemas.

    Do not hesitate to return 'N/A' if the 'creation_chat_messages' does not contain anything that is not included in the schemas."""


@workflowai.agent(
    id="input-generation-instructions",
    version=workflowai.VersionProperties(
        model=workflowai.Model.CLAUDE_3_7_SONNET_20250219,
        max_tokens=1000,
        instructions=INSTRUCTIONS,
    ),
)
async def run_input_generation_instructions(
    input: InputGenerationInstructionsInput,
) -> InputGenerationInstructionsOutput:
    """You are an instruction generation specialist focused on creating clear guidelines for input data generation that will be passed to another agent, the Input Generation Agent.

    Focus solely on extracting relevant information from the 'creation_chat_messages' (e.g., URLs to use), as the Input Generation Agent also has access to the agent_name and the input/output schemas.

    Do not hesitate to return 'N/A' if the 'creation_chat_messages' does not contain anything that is not included in the schemas."""
    ...
