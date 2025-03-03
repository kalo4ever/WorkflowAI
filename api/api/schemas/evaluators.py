from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field

from core.domain.field_based_evaluation_config import FieldBasedEvaluationConfig, UnsupportedSchema
from core.domain.task_evaluator import (
    EvaluatorMetric,
    EvaluatorTrigger,
    EvaluatorTypeName,
    FaithfulnessEvaluator,
    FieldBasedEvaluator,
    TaskEvaluator,
)
from core.domain.task_group_properties import TaskGroupProperties
from core.domain.task_variant import SerializableTaskVariant
from core.utils.schemas import InvalidSchemaError, JsonSchema


class AvailableEvaluator(BaseModel):
    metric: EvaluatorMetric
    triggers: set[EvaluatorTrigger]
    type: Union[EvaluatorTypeName, Literal["latency", "cost", "user"]]
    uses_examples: bool = False
    configurable: bool = False


TaskEvaluatorResponse = Union[AvailableEvaluator, TaskEvaluator]


class FieldBasedEvaluatorBuilder(BaseModel):
    """An evaluator that will compare the output of a run with the output of an
    associated example using field based comparisons"""

    type: Literal["field_based"]
    field_based_evaluation_config: FieldBasedEvaluationConfig

    def build(self, task: SerializableTaskVariant) -> FieldBasedEvaluator:
        output_schema = JsonSchema(schema=task.output_schema.json_schema)
        # Making sure the config matches the schema
        try:
            self.field_based_evaluation_config.options.supports_schema(output_schema)
        except UnsupportedSchema as e:
            kp = ".".join(e.keys)
            raise AssertionError(f"Unsupported evaluation config for task schema at {kp}: {str(e)}")

        return FieldBasedEvaluator(config=self.field_based_evaluation_config, type=self.type)


class FaithfulnessEvaluatorBuilder(BaseModel):
    type: Literal["faithfulness"]

    new_user_message_keypath: list[str | int] | None = Field(
        default=None,
        description="A keypath to describe where to find the new user message in the task input",
        min_length=1,
    )
    new_assistant_answer_keypath: list[str | int] | None = Field(
        default=None,
        description="A keypath to describe where to find the new assistant answer in the task output",
        min_length=1,
    )

    faithfulness_task_group_properties: TaskGroupProperties | None = None

    @classmethod
    def _find_string_schema(
        cls,
        prefixes: list[list[str | int]],
        schema: JsonSchema,
        suffixes: list[list[str | int]] | None = None,
    ) -> list[str | int]:
        suffixes = suffixes or [
            ["text"],
            ["content_text"],
        ]
        for keypath in prefixes:
            try:
                root_schema = schema.sub_schema(keypath)
            except InvalidSchemaError:
                continue

            if root_schema.type == "string":
                return keypath

            for suffix in suffixes:
                try:
                    schema = root_schema.sub_schema(suffix)
                    if schema.type == "string":
                        return keypath + suffix
                except InvalidSchemaError:
                    continue
        raise ValueError("Could not find a suitable keypath for new user message")

    @classmethod
    def find_new_user_message_keypath(cls, input_schema: JsonSchema) -> list[str | int]:
        return cls._find_string_schema(
            [
                ["new_user_message"],
                ["question"],
                ["conversation", -1],
                ["messages", -1],
                ["user_message"],
                ["user_messages"],
            ],
            input_schema,
        )

    @classmethod
    def find_new_assistant_answer_keypath(cls, output_schema: JsonSchema) -> list[str | int]:
        return cls._find_string_schema(
            [
                ["new_assistant_answer"],
                ["answer"],
                ["response"],
                ["content"],
                ["text"],
                ["content_text"],
            ],
            output_schema,
        )

    # TODO: test
    @classmethod
    def validate_key_path_string(cls, schema: JsonSchema, key_path: list[str | int]) -> list[str | int]:
        try:
            if not schema.sub_schema(key_path).type == "string":
                raise ValueError(f"Key path {key_path} does not point to a string schema")
            return key_path
        except InvalidSchemaError:
            raise ValueError(f"Key path {key_path} does not point to a valid schema")

    # TODO: test
    def build(self, task: SerializableTaskVariant) -> FaithfulnessEvaluator:
        input_schema = JsonSchema(schema=task.input_schema.json_schema)
        output_schema = JsonSchema(schema=task.output_schema.json_schema)

        new_user_message_keypath = (
            self.validate_key_path_string(input_schema, self.new_user_message_keypath)
            if self.new_user_message_keypath is not None
            else self.find_new_user_message_keypath(input_schema)
        )

        new_assistant_answer_keypath = (
            self.validate_key_path_string(output_schema, self.new_assistant_answer_keypath)
            if self.new_assistant_answer_keypath is not None
            else self.find_new_assistant_answer_keypath(output_schema)
        )

        return FaithfulnessEvaluator(
            type=self.type,
            new_user_message_keypath=new_user_message_keypath,
            new_assistant_answer_keypath=new_assistant_answer_keypath,
            faithfulness_task_group_properties=self.faithfulness_task_group_properties,
        )


EvaluatorBuilder = Annotated[
    Union[FieldBasedEvaluatorBuilder, FaithfulnessEvaluatorBuilder],
    Field(discriminator="type"),
]
