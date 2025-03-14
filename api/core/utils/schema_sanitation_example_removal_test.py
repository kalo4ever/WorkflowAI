from typing import Any

import pytest

from core.utils.schema_sanitation import (
    _remove_examples,  # pyright: ignore[reportPrivateUsage]
    _remove_examples_non_string_and_enum,  # pyright: ignore[reportPrivateUsage]
)


@pytest.mark.parametrize(
    "schema,expected",
    [
        # Test case 1: Properties with string, integer, and enum types
        (
            {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "examples": ["Alice", "Bob"],  # Should be KEPT
                    },
                    "age": {
                        "type": "integer",
                        "examples": [25, 30],  # Should be REMOVED
                    },
                    "status": {
                        "type": "string",
                        "enum": ["ACTIVE", "INACTIVE"],
                        "examples": ["ACTIVE"],  # Should be REMOVED
                    },
                },
            },
            {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "examples": ["Alice", "Bob"],  # Examples KEPT
                    },
                    "age": {
                        "type": "integer",
                        # Examples REMOVED
                    },
                    "status": {
                        "type": "string",
                        "enum": ["ACTIVE", "INACTIVE"],
                        # Examples REMOVED
                    },
                },
            },
        ),
        # Test case 2: Array and nested object properties
        (
            {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "examples": ["A sample description."],  # Should be KEPT
                    },
                    "tags": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "examples": ["tag1", "tag2"],  # Should be KEPT
                        },
                    },
                    "priority": {
                        "type": "integer",
                        "examples": [1, 2, 3],  # Should be REMOVED
                    },
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "created_by": {
                                "type": "string",
                                "examples": ["user1", "user2"],  # Should be KEPT
                            },
                            "timestamps": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "examples": ["2021-01-01T00:00:00Z", "2021-06-01T12:00:00Z"],  # Should be KEPT
                                },
                            },
                        },
                    },
                },
            },
            {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "examples": ["A sample description."],  # Examples KEPT
                    },
                    "tags": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "examples": ["tag1", "tag2"],  # Examples KEPT
                        },
                    },
                    "priority": {
                        "type": "integer",
                        # Examples REMOVED
                    },
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "created_by": {
                                "type": "string",
                                "examples": ["user1", "user2"],  # Examples KEPT
                            },
                            "timestamps": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "examples": ["2021-01-01T00:00:00Z", "2021-06-01T12:00:00Z"],  # Examples KEPT
                                },
                            },
                        },
                    },
                },
            },
        ),
        # Test case 3: Nested objects with mixed example preservation
        (
            {
                "type": "object",
                "properties": {
                    "project": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "examples": ["Project Alpha", "Project Beta"],  # Should be KEPT
                            },
                            "contributors": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "examples": ["Alice", "Bob"],  # Should be KEPT
                                        },
                                        "role": {
                                            "type": "string",
                                            "examples": ["Developer", "Designer"],  # Should be KEPT
                                        },
                                        "experience_years": {
                                            "type": "integer",
                                            "examples": [3, 5],  # Should be REMOVED
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "deadline": {
                        "type": "string",
                        "format": "date-time",
                        "examples": ["2023-12-31T23:59:59Z"],  # Should be KEPT
                    },
                },
            },
            {
                "type": "object",
                "properties": {
                    "project": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "examples": ["Project Alpha", "Project Beta"],  # Example KEPT
                            },
                            "contributors": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "examples": ["Alice", "Bob"],  # Should be KEPT
                                        },
                                        "role": {
                                            "type": "string",
                                            "examples": ["Developer", "Designer"],  # Should be KEPT
                                        },
                                        "experience_years": {
                                            "type": "integer",
                                            # Examples REMOVED
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "deadline": {
                        "type": "string",
                        "format": "date-time",
                        "examples": ["2023-12-31T23:59:59Z"],  # Examples KEPT
                    },
                },
            },
        ),
        # Test case 4: Enum and number types with examples to be removed
        (
            {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["A", "B", "C"],
                        "examples": ["A", "C"],  # Should be REMOVED
                    },
                    "rating": {
                        "type": "number",
                        "examples": [4.5, 3.8],  # Should be REMOVED
                    },
                    "details": {
                        "type": "object",
                        "properties": {
                            "manufacturer": {
                                "type": "string",
                                "examples": ["CompanyX", "CompanyY"],  # Should be KEPT
                            },
                            "warranty_years": {
                                "type": "integer",
                                "examples": [1, 2],  # Should be REMOVED
                            },
                        },
                    },
                },
            },
            {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["A", "B", "C"],
                        # Examples REMOVED
                    },
                    "rating": {
                        "type": "number",
                        # Examples REMOVED
                    },
                    "details": {
                        "type": "object",
                        "properties": {
                            "manufacturer": {
                                "type": "string",
                                "examples": ["CompanyX", "CompanyY"],
                            },
                            "warranty_years": {
                                "type": "integer",
                                # Examples REMOVED
                            },
                        },
                    },
                },
            },
        ),
        # Test case 5: Mixed types in arrays with examples conditionally removed
        (
            {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "string",
                                    "examples": ["item1", "item2"],  # Should be KEPT
                                },
                                "quantity": {
                                    "type": "integer",
                                    "examples": [10, 20],  # Should be REMOVED
                                },
                                "status": {
                                    "type": "string",
                                    "enum": ["AVAILABLE", "OUT_OF_STOCK"],
                                    "examples": ["AVAILABLE"],  # Should be REMOVED
                                },
                            },
                        },
                    },
                },
            },
            {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "string",
                                    "examples": ["item1", "item2"],
                                },
                                "quantity": {
                                    "type": "integer",
                                    # Examples REMOVED
                                },
                                "status": {
                                    "type": "string",
                                    "enum": ["AVAILABLE", "OUT_OF_STOCK"],
                                    # Examples REMOVED
                                },
                            },
                        },
                    },
                },
            },
        ),
        (
            {
                "type": "object",
                "properties": {
                    "examples": {
                        "type": "string",
                        "description": "Examples as a field",
                        "examples": ["This is an example", "This is another example"],
                    },
                    "some_other_field": {
                        "type": "number",
                        "examples": [1, 2, 3],
                    },
                },
            },
            {
                "type": "object",
                "properties": {
                    "examples": {
                        "type": "string",
                        "description": "Examples as a field",
                        "examples": ["This is an example", "This is another example"],  # Examples KEPT
                    },
                    "some_other_field": {
                        "type": "number",
                        # Examples REMOVED
                    },
                },
            },
        ),
    ],
)
def test_remove_examples_non_string_and_enum(schema: dict[str, Any], expected: dict[str, Any]) -> None:
    sanitized = _remove_examples_non_string_and_enum(schema)
    assert sanitized == expected


@pytest.mark.parametrize(
    "schema,expected",
    [
        # Test case 1: Basic schema with examples at root level
        (
            {
                "type": "object",
                "examples": [{"name": "John"}, {"name": "Jane"}],
                "properties": {
                    "name": {"type": "string"},
                },
            },
            {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                },
            },
        ),
        # Test case 2: Nested properties with examples
        (
            {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "examples": ["John", "Jane"],
                    },
                    "age": {
                        "type": "integer",
                        "examples": [25, 30],
                    },
                },
            },
            {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                    },
                    "age": {
                        "type": "integer",
                    },
                },
            },
        ),
        # Test case 3: Array items with examples
        (
            {
                "type": "object",
                "properties": {
                    "tags": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "examples": ["tag1", "tag2"],
                        },
                        "examples": [["tag1"], ["tag2"]],
                    },
                },
            },
            {
                "type": "object",
                "properties": {
                    "tags": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                },
            },
        ),
        # Test case 4: Schema with no examples
        (
            {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                },
            },
            {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                },
            },
        ),
        # Test case 5: Deeply nested objects with examples
        (
            {
                "type": "object",
                "properties": {
                    "user": {
                        "type": "object",
                        "examples": [{"name": "John", "details": {"age": 25}}],
                        "properties": {
                            "name": {
                                "type": "string",
                                "examples": ["John", "Jane"],
                            },
                            "details": {
                                "type": "object",
                                "examples": [{"age": 25}],
                                "properties": {
                                    "age": {
                                        "type": "integer",
                                        "examples": [25, 30],
                                    },
                                },
                            },
                        },
                    },
                },
            },
            {
                "type": "object",
                "properties": {
                    "user": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                            },
                            "details": {
                                "type": "object",
                                "properties": {
                                    "age": {
                                        "type": "integer",
                                    },
                                },
                            },
                        },
                    },
                },
            },
        ),
    ],
)
def test_remove_examples(schema: dict[str, Any], expected: dict[str, Any]) -> None:
    result = _remove_examples(schema)
    assert result == expected
