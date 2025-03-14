from typing import Any, AsyncIterator

import workflowai
from pydantic import BaseModel, Field


class SuggestedAgentInputOutputExampleInput(BaseModel):
    agent_description: str | None = Field(
        default=None,
        description="The description of what the agent does",
    )
    explaination: str | None = Field(
        default=None,
        description="The explanation of why the agent is useful for the company",
    )
    destination_department: str | None = Field(
        default=None,
        description="The department the agent is for",
    )
    input_json_schema: dict[str, Any] | None = Field(
        default=None,
        description="The JSON schema of the agent input",
    )
    output_json_schema: dict[str, Any] | None = Field(
        default=None,
        description="The JSON schema of the agent output",
    )


class SuggestedAgentInputOutputExampleOutput(BaseModel):
    agent_input_example: dict[str, Any] | None = Field(
        default=None,
        description="An example that illustrates the agent input (enforcing the 'input_json_schema')",
    )
    agent_output_example: dict[str, Any] | None = Field(
        default=None,
        description="An example that illustrates the agent output (enforcing the 'output_json_schema')",
    )


@workflowai.agent(id="suggested-task-output-example", model=workflowai.Model.CLAUDE_3_7_SONNET_20250219)
def stream_suggested_agent_input_output_example(
    input: SuggestedAgentInputOutputExampleInput,
) -> AsyncIterator[SuggestedAgentInputOutputExampleOutput]:
    """You are a business analyst specializing in agent documentation and specification.

    Your goal is to analyze the input data containing:

    - an agent description
    - an explanation
    - department assignment
    - input JSON schema
    - output JSON schema

    and generate representative example input and output objects. Indeed the input and output must be linked in the sense that the input would have realistically yield the output.

    Both examples must strictly conform to their respective JSON schemas (input_json_schema and output_json_schema) while realistically demonstrating what the task input and output would look like."""
    ...
