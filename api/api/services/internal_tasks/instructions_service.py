import logging
from typing import AsyncIterator

from core.agents.task_instruction_tool_update_task import (
    TaskInstructionsToolUpdateTaskInput,
    TaskInstructionsToolUpdateTaskOutput,
    stream_task_instruction_tool_update,
)
from core.domain.task_variant import SerializableTaskVariant
from core.domain.tool import Tool
from core.runners.workflowai.workflowai_runner import WorkflowAIRunner
from core.tools import ToolKind, is_handle_in

_logger = logging.getLogger()


class InstructionsService:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    # TODO: migrate all instructions-related methods from the InternalTasksService to this service.

    @classmethod
    def get_tools_to_remove(cls, instructions: str, selected_tools: list[ToolKind]) -> list[str]:
        return [
            tool_handle
            for tool_handle in ToolKind
            if tool_handle not in selected_tools and is_handle_in(instructions, tool_handle)
        ]

    @classmethod
    def get_tools_to_add(cls, instructions: str, selected_tools: list[ToolKind]) -> list[Tool]:
        return [
            WorkflowAIRunner.internal_tools[tool_handle].definition
            for tool_handle in selected_tools
            if not is_handle_in(instructions, tool_handle)
        ]

    async def update_task_instructions(
        self,
        task_variant: SerializableTaskVariant,
        instructions: str,
        selected_tools: list[ToolKind],
    ) -> AsyncIterator[TaskInstructionsToolUpdateTaskOutput]:
        task_input = TaskInstructionsToolUpdateTaskInput(
            task=TaskInstructionsToolUpdateTaskInput.Task(
                name=task_variant.name,
                input_json_schema=task_variant.input_schema.json_schema,
                output_json_schema=task_variant.output_schema.json_schema,
            ),
            initial_task_instructions=ToolKind.replace_tool_aliases_with_handles(instructions),
            tools_to_remove=self.get_tools_to_remove(instructions, selected_tools),
            tools_to_add=[
                TaskInstructionsToolUpdateTaskInput.Tool.from_domain_tool(tool)
                for tool in self.get_tools_to_add(instructions, selected_tools)
            ],
        )

        return stream_task_instruction_tool_update(task_input, use_cache="always")
