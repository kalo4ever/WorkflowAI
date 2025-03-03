from typing import Literal

from pydantic import BaseModel, Field

INTERNAL_AGENT_RUN_RESULT_SCHEMA_KEY = "internal_agent_run_result"


class AgentRunError(BaseModel):
    error_code: Literal["tool_call_error", "missing_tool", "other"] | None = Field(
        default=None,
        description="The type of error that occurred during the agent run, 'tool_call_error' if an error occurred during a tool call, 'missing_tool' if the agent is missing a tool in order to complete the run, 'other' for any other error",
    )
    error_message: str | None = Field(
        default=None,
        description="A summary of the error that occurred during the agent run",
    )


class AgentRunResult(BaseModel):
    status: Literal["success", "failure"] | None = Field(
        default=None,
        description="Whether the agent run was successful or not",
    )

    error: AgentRunError | None = Field(
        default=None,
        description="The error that occurred during the agent run, to fill in case of status='failure'",
    )
