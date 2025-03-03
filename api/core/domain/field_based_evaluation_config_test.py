import pytest

from core.utils.schemas import JsonSchema

from .field_based_evaluation_config import (
    ArrayComparisonOptions,
    BaseComparisonOptions,
    BooleanComparisonOptions,
    FieldBasedEvaluationConfig,
    NumberComparisonOptions,
    ObjectComparisonOptions,
    StringComparisonOptions,
    UnsupportedSchema,
)


def test_field_evaluation_options_deser() -> None:
    raw = {
        "options": {
            "type": "object",
            "property_evaluations": {
                "a": {"type": "string", "semantics": True},
                "b": {"type": "number", "delta": 1},
                "c": {"type": "boolean", "ignore": True},
                "d": {
                    "type": "array",
                    "element_evaluation": {"type": "string", "fuzzy": True},
                    "ignore_order": True,
                },
            },
        },
        "default_semantic_matching_group_properties": {"temperature": 1},
    }

    # Check that we can parse the object correctly
    config = FieldBasedEvaluationConfig.model_validate(raw)
    assert isinstance(config.options, ObjectComparisonOptions)
    assert config.options.property_evaluations is not None
    assert isinstance(config.options.property_evaluations["a"], StringComparisonOptions)
    assert config.options.property_evaluations["a"].semantics


@pytest.fixture(scope="function")
def all_comparison_types() -> list[type[BaseComparisonOptions]]:
    return [
        ArrayComparisonOptions,
        BooleanComparisonOptions,
        NumberComparisonOptions,
        ObjectComparisonOptions,
        StringComparisonOptions,
    ]


def test_init(all_comparison_types: list[type[BaseComparisonOptions]]) -> None:
    # Check that we can create an instance of each comparison type
    # without any param
    for comparison_type in all_comparison_types:
        comparison_type()


class TestSupportsSchema:
    def test_success(self, schema_2: JsonSchema):
        config = FieldBasedEvaluationConfig(
            options=ObjectComparisonOptions(
                property_evaluations={
                    "name1": StringComparisonOptions(),
                    # Voluntarily omitted
                    # "description": StringComparisonOptions(type="string"),
                    "opt_description": StringComparisonOptions(),
                    "price": NumberComparisonOptions(),
                    "in_stock": BooleanComparisonOptions(),
                    "sub2": ArrayComparisonOptions(
                        element_evaluation=ObjectComparisonOptions(
                            property_evaluations={
                                "key3": StringComparisonOptions(),
                            },
                        ),
                    ),
                    "string_array": ArrayComparisonOptions(),
                    "sub1": ObjectComparisonOptions(
                        property_evaluations={
                            "key2": NumberComparisonOptions(),
                        },
                    ),
                },
            ),
        )

        config.options.supports_schema(schema_2)

    def test_invaid_field(self, schema_2: JsonSchema):
        config = FieldBasedEvaluationConfig(
            options=ObjectComparisonOptions(
                property_evaluations={
                    "optdescription": StringComparisonOptions(),
                },
            ),
        )

        with pytest.raises(UnsupportedSchema) as e:
            config.options.supports_schema(schema_2)

        assert e.value.keys == ["optdescription"]

    def test_invaid_nested(self, schema_2: JsonSchema):
        config = FieldBasedEvaluationConfig(
            options=ObjectComparisonOptions(
                property_evaluations={
                    "sub2": ArrayComparisonOptions(
                        element_evaluation=ObjectComparisonOptions(
                            property_evaluations={
                                "key3": BooleanComparisonOptions(),
                            },
                        ),
                    ),
                },
            ),
        )

        with pytest.raises(UnsupportedSchema) as e:
            config.options.supports_schema(schema_2)

        assert e.value.keys == ["sub2", "$", "key3"]

    def test_missing_type(self, schema_3: JsonSchema) -> None:
        config = FieldBasedEvaluationConfig(
            options=ObjectComparisonOptions(
                property_evaluations={
                    "sorted_cities": ArrayComparisonOptions(
                        element_evaluation=StringComparisonOptions(),
                    ),
                },
            ),
        )
        config.options.supports_schema(schema_3)
