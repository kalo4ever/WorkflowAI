from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

from core.domain.task_io import SerializableTaskIO

TaskInput = TypeVar("TaskInput", bound=BaseModel)
TaskOutput = TypeVar("TaskOutput", bound=BaseModel)


class Task(BaseModel, Generic[TaskInput, TaskOutput]):
    """
    A blueprint for a task. Used to instantiate task runs
    Default values are provided so that they can be overriden in subclasses
    """

    # Providing defaults so they can be overriden in subclasses
    name: str = ""
    input_class: type[TaskInput] = BaseModel  # type: ignore
    output_class: type[TaskOutput] = BaseModel  # type: ignore
    instructions: str = Field(default="", validate_default=True, description="Instructions for the task")
    schema_id: int = Field(
        default=0,
        description="""An int identifier of the schema version. It is incremented every time
        the json schema (excluding metadata) of the input / output changes. In other words,
        it is a short hand for the pair input_class.schema_version / output_class.schema_version""",
    )

    def id(self) -> str:
        """A unique identifier for the task, used to identify the task class.
        Override to provide a custom ID, for example if the task class definition
        gets renamed."""
        return self.name.lower()

    def validate_output(
        self,
        output: Any,
        partial: bool = False,
        strip_extras: bool = True,
    ) -> TaskOutput:
        if partial:
            return self.output_class.model_construct(None, **output)

        return self.output_class.model_validate(output)

    def to_serializable(self):
        from core.domain.task_variant import SerializableTaskVariant

        return SerializableTaskVariant(
            task_id=self.id(),
            id="",
            name=self.name,
            task_schema_id=self.schema_id,
            input_schema=SerializableTaskIO.from_model(self.input_class),
            output_schema=SerializableTaskIO.from_model(self.output_class),
        )
