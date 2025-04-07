import workflowai
from pydantic import BaseModel, Field


class SuggestedAgentValidationInput(BaseModel):
    instructions: str | None = Field(
        default=None,
        description="The instructions the agent suggestion agent must follow",
    )
    proposed_agent_name: str | None = Field(
        default=None,
        description="The name of the proposed agent",
    )


class SuggestedAgentValidationOutput(BaseModel):
    reason: str | None = Field(
        default=None,
        description="The reason why the agent is not valid or invalid",
    )
    enforces_instructions: bool | None = Field(
        default=None,
        description="Whether the agent enforces the instructions",
    )
    is_customer_facing: bool | None = Field(
        default=None,
        description="Whether the agent is customer facing",
    )
    requires_llm_capabilities: bool | None = Field(
        default=None,
        description="Whether the agent requires LLM capabilities, a good way to check this is to ask yourself if the agent can be handled with (deterministic) code or could have existed in year 2020",
    )


INSTRUCTIONS = """
You are an expert at evaluating if suggested agents enforce exactly the instructions that are provided.
"""


@workflowai.agent(
    id="suggested-agent-validation-agent",
    version=workflowai.VersionProperties(
        model=workflowai.Model.GEMINI_2_0_FLASH_001,  # Nice mix between creativity and focus on the instructions
        instructions=INSTRUCTIONS,
        temperature=0.0,  # Stability
    ),
)
async def run_suggested_agent_validation(
    input: SuggestedAgentValidationInput,
) -> SuggestedAgentValidationOutput: ...
