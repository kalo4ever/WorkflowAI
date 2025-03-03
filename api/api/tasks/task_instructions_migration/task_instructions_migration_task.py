from typing import AsyncIterator

import workflowai
from pydantic import BaseModel, Field

from api.tasks.chat_task_schema_generation.chat_task_schema_generation_task import AgentSchemaJson
from core.domain.fields.chat_message import ChatMessage
from core.domain.models import Model


class TaskInstructionsMigrationTaskInput(BaseModel):
    initial_task_schema: AgentSchemaJson = Field(description="The task to generate the instructions for")
    initial_task_instructions: str = Field(description="The initial instructions of the task")

    chat_messages: list[ChatMessage] = Field(
        description="The chat messages that originated the update of the task schema",
    )
    new_task_schema: AgentSchemaJson = Field(description="The new task schema")

    available_tools_description: str = Field(
        description="The description of the available tools, potientially available for the task we are generating the schema for",
    )


class TaskInstructionsMigrationTaskOutput(BaseModel):
    new_task_instructions: str = Field(default="", description="The new instructions on how to complete the task")


@workflowai.agent(id="task-instructions-migration", model=Model.CLAUDE_3_7_SONNET_20250219)
def stream_task_instructions_update(
    input: TaskInstructionsMigrationTaskInput,
) -> AsyncIterator[TaskInstructionsMigrationTaskOutput]:
    """Your goal is to generate 'new_task_instructions' based on 'initial_task_instructions',  'initial_task_schema' and 'new_task_schema'.

    To do so, think step by step:
    - First, define what are the noticeable 'diffs' between the 'initial_task_schema' and the 'new_task_schema' (DO NOT output any JSON part describing those diffs, outside of the task output schema that you need to enforce)
    - Based only on those 'diffs', update the instruction, for example by: deleting content (in case of deleted properties) / updating content (in case of rename or updated properties) or adding content (in case an important part has been added to the schema).

    Overall, keep as much as possible of the initial instructions (content and form), and use the same verbosity. Do NOT use markdown.

    Make sure to NOT add tools from 'available_tools_description' that were not present in the 'initial_task_instructions'"""
    ...


@workflowai.agent(id="task-instructions-migration", model=Model.CLAUDE_3_7_SONNET_20250219)
async def update_task_instructions(
    input: TaskInstructionsMigrationTaskInput,
) -> TaskInstructionsMigrationTaskOutput:
    """Your goal is to generate 'new_task_instructions' based on 'initial_task_instructions',  'initial_task_schema' and 'new_task_schema'.

    To do so, think step by step:
    - First, define what are the noticeable 'diffs' between the 'initial_task_schema' and the 'new_task_schema' (DO NOT output any JSON part describing those diffs, outside of the task output schema that you need to enforce)
    - Based only on those 'diffs', update the instruction, for example by: deleting content (in case of deleted properties) / updating content (in case of rename or updated properties) or adding content (in case an important part has been added to the schema).

    Overall, keep as much as possible of the initial instructions (content and form), and use the same verbosity. Do NOT use markdown.

    Make sure to NOT add tools from 'available_tools_description' that were not present in the 'initial_task_instructions'"""
    ...
