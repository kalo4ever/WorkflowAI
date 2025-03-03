from typing import Any

import pytest

from core.utils.schema_utils import json_schema_from_json


@pytest.mark.parametrize(
    "data, expected_schema",
    [
        (
            {"name": "John", "age": 30},
            {
                "type": "object",
                "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
            },
        ),
        (
            {"items": [1, 2, 3]},
            {
                "type": "object",
                "properties": {"items": {"type": "array", "items": {"type": "integer"}}},
            },
        ),
        (
            {"nested": {"key": "value"}},
            {
                "type": "object",
                "properties": {
                    "nested": {"type": "object", "properties": {"key": {"type": "string"}}},
                },
            },
        ),
        (
            {
                "id": 1234,
                "name": "Complex Example",
                "active": True,
                "metadata": None,
                "tags": ["important", "test", "complex"],
                "config": {
                    "enabled": True,
                    "timeout": 30,
                    "retries": 3,
                },
                "items": [
                    {
                        "id": 1,
                        "name": "First Item",
                        "color": "red",
                        "size": "large",
                        "measurements": [10.5, 20.1, 30.8],
                        "available": True,
                    },
                    {
                        "id": 2,
                        "name": "Second Item",
                        "color": "blue",
                        "size": "medium",
                        "available": False,
                        "related_items": [
                            {"id": 101, "relation": "similar"},
                            {"id": 102, "relation": "alternative"},
                        ],
                    },
                ],
                "empty": {},
            },
            {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "active": {"type": "boolean"},
                    "metadata": {"type": "null"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "config": {
                        "type": "object",
                        "properties": {
                            "enabled": {"type": "boolean"},
                            "timeout": {"type": "integer"},
                            "retries": {"type": "integer"},
                        },
                    },
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"},
                                "color": {"type": "string"},
                                "size": {"type": "string"},
                                "measurements": {
                                    "type": "array",
                                    "items": {"type": "number"},
                                },
                                "available": {"type": "boolean"},
                                "related_items": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "relation": {"type": "string"},
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "empty": {"type": "object"},
                },
            },
        ),
    ],
)
def test_json_schema_from_json(data: dict[str, Any], expected_schema: dict[str, Any]) -> None:
    schema = json_schema_from_json(data)
    assert schema == expected_schema
