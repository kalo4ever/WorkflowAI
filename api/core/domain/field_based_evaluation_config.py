from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field
from typing_extensions import override

from core.domain.task_group_properties import TaskGroupProperties
from core.utils.schemas import InvalidSchemaError, JsonSchema


class UnsupportedSchema(Exception):
    def __init__(self, message: str, keys: list[str]):
        super().__init__(message)
        self.keys = keys


class BaseComparisonOptions(BaseModel):
    ignore: bool = False

    def supports_schema(self, schema: JsonSchema):
        # ok to ignore, all children have a type
        if self.type != schema.type:  # type: ignore
            raise UnsupportedSchema(f"Schema type {schema.type} is not supported", [])


class StringComparisonOptions(BaseComparisonOptions):
    """Options to compare strings. By default, punctuation, accents, and case are ignored."""

    type: Literal["string"] = "string"

    semantics: Optional[bool] = Field(
        default=None,
        description="Whether to compare the semantics of the strings instead of the exact values",
    )

    case_sensitive: Optional[bool] = Field(
        default=None,
        description="Whether to compare the strings in a case sensitive way",
    )

    strict_equality: Optional[bool] = Field(
        default=None,
        description="If set to true, strings will be expected to match exactly.",
    )


class NumberComparisonOptions(BaseComparisonOptions):
    type: Literal["number"] = "number"

    delta: Optional[int] = Field(
        default=None,
        description="The maximum difference allowed between the expected and actual value."
        "If not provided an exact match is required",
    )

    @override
    def supports_schema(self, schema: JsonSchema):
        if schema.type == "number" or schema.type == "integer":
            return
        raise UnsupportedSchema(f"Schema type {schema.type} is not supported", [])


class BooleanComparisonOptions(BaseComparisonOptions):
    type: Literal["boolean"] = "boolean"


class ObjectComparisonOptions(BaseComparisonOptions):
    type: Literal["object"] = "object"

    strict_equality: Optional[bool] = Field(
        default=None,
        description="Whether to compare the object for strict equality. "
        "Setting this to true will skip the comparison for the object's fields",
    )

    property_evaluations: Optional[dict[str, "FieldComparisonOptions"]] = Field(
        default=None,
        description="The evaluations for the object's properties. Required if strict_equality is not true",
    )

    def supports_schema(self, schema: JsonSchema):
        super().supports_schema(schema)

        if not self.property_evaluations:
            return

        for key, value in self.property_evaluations.items():
            try:
                child_schema = schema.child_schema(key, splat_nulls=True)
                try:
                    value.supports_schema(child_schema)
                except UnsupportedSchema as e:
                    e.keys.insert(0, key)
                    raise e

            except InvalidSchemaError:
                raise UnsupportedSchema("Keypath does not exist in json schema", [key])


class ArrayComparisonOptions(BaseComparisonOptions):
    type: Literal["array"] = "array"

    strict_equality: Optional[bool] = Field(
        default=None,
        description="Whether to compare the array for strict equality. "
        "Setting this to true will skip the comparison for the array's elements",
    )

    element_evaluation: Optional["FieldComparisonOptions"] = Field(
        default=None,
        description="The evaluation for the array's elements, required if strict_equality is not true",
    )

    ignore_order: Optional[bool] = Field(
        default=None,
        description="Whether to ignore the order of the elements in the array "
        "If set to true, the computed score will be 1 if there is a set of pairs of distinct elements "
        "that each have a score of 1",
    )

    def supports_schema(self, schema: JsonSchema):
        super().supports_schema(schema)

        if not self.element_evaluation:
            return

        try:
            child_schema = schema.child_schema("0", splat_nulls=True)
            try:
                self.element_evaluation.supports_schema(child_schema)
            except UnsupportedSchema as e:
                e.keys.insert(0, "$")
                raise e

        except InvalidSchemaError:
            raise UnsupportedSchema("Keypath does not exist in json schema", ["$"])


FieldComparisonOptions = Annotated[
    Union[
        StringComparisonOptions,
        NumberComparisonOptions,
        BooleanComparisonOptions,
        ObjectComparisonOptions,
        ArrayComparisonOptions,
    ],
    Field(discriminator="type"),
]


class FieldBasedEvaluationConfig(BaseModel):
    options: FieldComparisonOptions

    default_semantic_matching_group_properties: Optional[TaskGroupProperties] = None
