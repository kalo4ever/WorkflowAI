from typing import Any

import pytest

from core.utils.schema_validation_utils import fix_non_object_root


@pytest.mark.parametrize(
    "schema,expected_schema,expected_is_fixed",
    [
        (
            {"type": "object", "properties": {"name": {"type": "string"}}},
            {"type": "object", "properties": {"name": {"type": "string"}}},
            False,
        ),
        (
            {"type": "array", "items": {"type": "string"}},
            {
                "type": "object",
                "properties": {"items": {"type": "array", "items": {"type": "string"}}},
                "required": ["items"],
            },
            True,
        ),
        (
            {"type": "string"},
            {"type": "object", "properties": {"output": {"type": "string"}}, "required": ["output"]},
            True,
        ),
        (
            {"type": "number"},
            {"type": "object", "properties": {"output": {"type": "number"}}, "required": ["output"]},
            True,
        ),
        (
            {"type": "boolean"},
            {"type": "object", "properties": {"output": {"type": "boolean"}}, "required": ["output"]},
            True,
        ),
        (
            {  # Real life use case from https://linear.app/workflowai/issue/WOR-2504/output-is-blank
                "dietary_restrictions_and_allergies": {
                    "description": "A summary of the patient's dietary restrictions and allergies without using the patient's name.",
                },
                "food_preferences": {
                    "description": "A summary of the patient's food preferences without using the patient's name.",
                },
                "calorie_and_macro_requirements": {
                    "description": "A summary of the patient's calorie and macronutrient requirements without using the patient's name.",
                },
                "household_considerations": {
                    "description": "Any household considerations that may affect meal planning without using the patient's name.",
                },
                "other_guidance": {
                    "description": "Any additional guidance or information relevant to meal planning without using the patient's name.",
                },
            },
            {
                "type": "object",
                "properties": {
                    "dietary_restrictions_and_allergies": {
                        "description": "A summary of the patient's dietary restrictions and allergies without using the patient's name.",
                    },
                    "food_preferences": {
                        "description": "A summary of the patient's food preferences without using the patient's name.",
                    },
                    "calorie_and_macro_requirements": {
                        "description": "A summary of the patient's calorie and macronutrient requirements without using the patient's name.",
                    },
                    "household_considerations": {
                        "description": "Any household considerations that may affect meal planning without using the patient's name.",
                    },
                    "other_guidance": {
                        "description": "Any additional guidance or information relevant to meal planning without using the patient's name.",
                    },
                },
            },
            True,
        ),
        (
            {"type": "string"},
            {"type": "object", "properties": {"output": {"type": "string"}}, "required": ["output"]},
            True,
        ),
    ],
)
def test_fix_non_object_root(schema: dict[str, Any], expected_schema: dict[str, Any], expected_is_fixed: bool) -> None:
    fixed_schema, is_fixed = fix_non_object_root(schema)
    assert fixed_schema == expected_schema
    assert is_fixed == expected_is_fixed
