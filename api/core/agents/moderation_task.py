from enum import Enum
from typing import Any

import workflowai
from pydantic import BaseModel, Field
from workflowai import Model

from core.domain.fields.chat_message import ChatMessage


class TaskVersionModerationInput(BaseModel):
    chat_messages: list[ChatMessage] | None = Field(
        default=None,
        description="The chat messages between the user and the task creation agent, that ocurred when the task was created",
    )
    task_name: str | None = Field(description="The name of the task")
    task_instructions: str | None = Field(description="The instructions of the task")
    task_input_schema: dict[str, Any] | None = Field(description="The input schema of the task")
    task_output_schema: dict[str, Any] | None = Field(description="The output schema of the task")


class TaskRunModerationInput(BaseModel):
    task_run_input: dict[str, Any] | None = Field(description="The input of the task run to moderate")


class ModerationOutput(BaseModel):
    reason: str | None = Field(default=None, description="The reason for the 'ris_task_breaching_terms' result")
    is_breaching_terms: bool | None = Field(default=None, description="Whether the task is breaching terms")

    class TermBreachingCategory(Enum):
        HATE = "HATE"
        SEXUALLY_EXPLICIT = "SEXUALLY_EXPLICIT"
        HARASSMENT = "HARASSMENT"
        DANGEROUS_CONTENT = "DANGEROUS_CONTENT"
        SCAM = "SCAM"
        SPAM = "SPAM"
        ILLEGAL_ACTIVITY = "ILLEGAL_ACTIVITY"
        MISINFORMATION = "MISINFORMATION"
        SELF_HARM = "SELF_HARM"
        MALICIOUS_SOFTWARE = "MALICIOUS_SOFTWARE"
        FRAUD = "FRAUD"
        OTHER = "OTHER"

    term_breaching_category: TermBreachingCategory | None = Field(
        default=None,
        description="The category of the breaching cause",
    )


@workflowai.agent(
    id="task-version-moderation",
    model=Model.GEMINI_1_5_PRO_002,
)
async def run_task_version_moderation_task(input: TaskVersionModerationInput) -> ModerationOutput:
    """You are a content moderation specialist responsible for evaluating tasks for potential terms of service violations. Your goal is to analyze the provided task information including its name, instructions, input/output schemas, and any associated chat messages to determine if it breaches terms of service. You must output:

    - A boolean indicating if the task breaches terms (is_task_breaching_terms)
    - If breaching, provide the specific violation category from the defined list (term_breaching_category)
    - A clear explanation of the reasoning behind your decision (reason)

    Look for content that could be considered:
    - Hate speech
    - Sexually explicit
    - Harassment
    - Dangerous
    - Scams
    - Spam
    - Illegal activities
    - Misinformation
    - Self-harm promotion
    - Malicious software
    - Fraud
    - Other violations

    Evaluate all components thoroughly and provide a well-reasoned determination focused on protecting users while allowing legitimate tasks to proceed."""
    ...


@workflowai.agent(
    id="task-run-moderation",
    model=Model.GEMINI_1_5_FLASH_002,
)
async def run_task_run_moderation_task(input: TaskRunModerationInput) -> ModerationOutput:
    """You are a content moderation expert responsible for evaluating task inputs for potential terms of service violations. Your task is to analyze the provided task_run_input to determine if it contains any content that breaches terms of service. You must provide:

    - A boolean value indicating if the content breaches terms (is_breaching_terms).
    - If terms are breached, specify the category from:
      - HATE
      - SEXUALLY_EXPLICIT
      - HARASSMENT
      - DANGEROUS_CONTENT
      - SCAM
      - SPAM
      - ILLEGAL_ACTIVITY
      - MISINFORMATION
      - SELF_HARM
      - MALICIOUS_SOFTWARE
      - FRAUD
      - OTHER
    - If terms are breached, provide a clear explanation of the violation in the reason field."""
    ...
