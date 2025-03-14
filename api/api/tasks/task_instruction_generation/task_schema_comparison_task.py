from pydantic import BaseModel, Field

from api.tasks.chat_task_schema_generation.chat_task_schema_generation_task import AgentSchemaJson
from core.domain.deprecated.task import Task


class TaskSchemaComparisonTaskInput(BaseModel):
    reference_schema: AgentSchemaJson
    candidate_schema: AgentSchemaJson


class TaskSchemaComparisonTaskOutput(BaseModel):
    differences_summary: str = Field(
        default="",
        description="A written summary of the differences between the reference and candidate TaskSchemas",
    )


class TaskSchemaComparisonTask(Task[TaskSchemaComparisonTaskInput, TaskSchemaComparisonTaskOutput]):
    name: str = "TaskSchemaComparison"
    input_class: type[TaskSchemaComparisonTaskInput] = TaskSchemaComparisonTaskInput
    output_class: type[TaskSchemaComparisonTaskOutput] = TaskSchemaComparisonTaskOutput
    instructions: str = """Analyze the reference TaskSchema and the candidate TaskSchema provided, and summarizes the main differences between them."""
