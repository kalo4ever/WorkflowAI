from typing import Any

import pytest

from core.storage.mongo.models.tool_call_schema import ToolCallResultSchema, ToolCallSchema


class TestToolCallSchema:
    @pytest.mark.parametrize(
        "payload",
        [
            {},
            {"id": "1", "tool_name": "tool_name", "tool_input_dict": {"key": "value"}},
        ],
    )
    def test_from_domain(self, payload: dict[str, Any]):
        # Check we don't return validation errors
        assert ToolCallSchema.model_validate(payload).to_domain()


class TestToolCallResultSchema:
    @pytest.mark.parametrize(
        "payload",
        [
            {},
            {"id": "1", "tool_name": "tool_name", "tool_input_dict": {"key": "value"}},
            {"id": "1", "tool_name": "tool_name", "tool_input_dict": {"key": "value"}, "result": "result"},
            {"id": "1", "tool_name": "tool_name", "tool_input_dict": {"key": "value"}, "error": "error"},
        ],
    )
    def test_from_domain(self, payload: dict[str, Any]):
        # Check we don't return validation errors
        assert ToolCallResultSchema.model_validate(payload).to_domain()
