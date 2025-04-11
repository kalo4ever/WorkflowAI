import workflowai
from pydantic import BaseModel, Field


class MetaAgentUserConfirmationInput(BaseModel):
    assistant_message_content: str = Field(
        description="The content of the message sent by the assistant that potentially contains a tool call.",
    )


class MetaAgentUserConfirmationOutput(BaseModel):
    requires_user_confirmation: bool = Field(
        description="True if the assistant's message explicitly or implicitly asks for user confirmation before proceeding with an action or tool call, False otherwise.",
    )


@workflowai.agent(
    model=workflowai.Model.GEMINI_2_0_FLASH_001,
)
async def meta_agent_user_confirmation_agent(
    input: MetaAgentUserConfirmationInput,
) -> MetaAgentUserConfirmationOutput:
    """Analyze the provided assistant message content. Determine if the message asks the user for confirmation before proceeding with a proposed action or tool call. Look for explicit questions like 'Should I proceed?', 'Do you want me to run this?', or phrases implying confirmation is needed like 'Let me know if you want to...', 'Click the button below to...', 'If you agree, I can...'.

    Return true if confirmation is required, false otherwise."""
    ...
