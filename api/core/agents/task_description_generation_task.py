from typing import AsyncIterator

import workflowai
from pydantic import BaseModel, Field

from core.domain.fields.chat_message import ChatMessage

from .chat_task_schema_generation.chat_task_schema_generation_task import AgentSchemaJson


class TaskDescriptionGenerationTaskInput(BaseModel):
    chat_messages: list[ChatMessage]

    task_schema: AgentSchemaJson = Field(description="The task for which a description needs to be generated.")

    task_instructions: str = Field(
        description="Instructions for how to complete the task.",
    )


class TaskDescriptionGenerationTaskOutput(BaseModel):
    task_description: str = Field(
        default="",
        description="A concise description of what the task accomplishes, based on the provided task input schema, and output schema.",
    )


@workflowai.agent(
    id="task-description-generation",
    version=workflowai.VersionProperties(
        model=workflowai.Model.CLAUDE_3_7_SONNET_20250219,
        max_tokens=500,
        instructions="""You are a task analysis assistant specializing in understanding and describing task specifications.

    Given a task schema containing input and output specifications, along with any task instructions, analyze these components to generate a concise, one-sentence description of what the task accomplishes. The 'task_description' must be a maximum of 80 characters.

    The descriptions for tasks should mirror the content of the opening line of 'task_instructions', minus the "You are…" at the start. For example:

    - Opening line: You are a medical scribe assistant specializing in converting medical transcripts into structured SOAP notes.
    'task_description': An AI agent specializing in converting medical transcripts into structured SOAP notes.
    - Opening line: You are a text summarization expert skilled in creating concise and accurate summaries.
    'task_description': An AI agent skilled in creating concise and accurate summaries.

    The description should be clear, action-oriented, and focus on the main purpose of the task. The term AI agent must be used.

    Avoid technical details about the schema structure itself and instead focus on the functional purpose of the task.""",
    ),
)
def stream_task_description_generation(
    task_input: TaskDescriptionGenerationTaskInput,
) -> AsyncIterator[TaskDescriptionGenerationTaskOutput]: ...
