from collections.abc import AsyncIterator
from typing import Any

import workflowai
from pydantic import BaseModel, Field
from workflowai import Model


class TaskInputImportTaskInput(BaseModel):
    task_name: str | None = Field(default=None, description="The name of the task that the input(s) belongs to")
    input_json_schema: dict[str, Any] | None = Field(
        default=None,
        description="The JSON schema for the input(s) of the task",
    )
    raw_input_data: str | None = Field(
        default=None,
        description="The raw input data to format as JSON object(s) conforming to the 'input_json_schema'.",
    )


class TaskInputImportTaskOutput(BaseModel):
    extracted_task_inputs: list[dict[str, Any]] | None = Field(
        default=None,
        description="JSON object(s) conforming to the 'input_json_schema', extracted from the 'raw_input_data'.",
    )


@workflowai.agent(id="task-input-import", model=Model.GEMINI_1_5_PRO_002)
async def task_input_import(input: TaskInputImportTaskInput) -> TaskInputImportTaskOutput:
    """Ensure that your output fully conforms to the 'original_output_schema' and that all required fields are completely and correctly populated. Pay special attention to the fact that 'extracted_task_inputs' is a list; hence, if the 'input_json_schema' root is a list, you will need to output a list of lists in 'extracted_task_inputs'. Make sure that your final output is complete and includes all necessary data."""
    ...


# TODO: replace with task_input_import.stream
@workflowai.agent(
    id="task-input-import",
    model=Model.GEMINI_1_5_PRO_002,
)
def stream_task_inputs_import_task(
    input: TaskInputImportTaskInput,
) -> AsyncIterator[TaskInputImportTaskOutput]:
    """Ensure that your output fully conforms to the 'original_output_schema' and that all required fields are completely and correctly populated. Pay special attention to the fact that 'extracted_task_inputs' is a list; hence, if the 'input_json_schema' root is a list, you will need to output a list of lists in 'extracted_task_inputs'. Make sure that your final output is complete and includes all necessary data."""
    ...
