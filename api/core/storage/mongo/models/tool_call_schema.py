from typing import Any

from pydantic import BaseModel

from core.domain.tool_call import ToolCall, ToolCallRequestWithID


class ToolCallSchema(BaseModel):
    id: str | None = None  # some old data has no id
    tool_name: str | None = None  # some old data has no tool_name
    tool_input_dict: dict[str, Any] | None = None  # some old data has no tool_input_dict

    @classmethod
    def from_domain(cls, tool_call: ToolCallRequestWithID):
        return cls(id=tool_call.id, tool_name=tool_call.tool_name, tool_input_dict=tool_call.tool_input_dict)

    def to_domain(self):
        return (
            ToolCallRequestWithID(
                id=self.id or "",
                tool_name=self.tool_name or "",
                tool_input_dict=self.tool_input_dict or {},
            )
            or {}
        )


class ToolCallResultSchema(ToolCallSchema):
    result: Any | None = None
    error: str | None = None

    @classmethod
    def from_domain(cls, tool_call: ToolCall):  # pyright: ignore [reportIncompatibleMethodOverride]
        return cls(
            id=tool_call.id,
            tool_name=tool_call.tool_name,
            tool_input_dict=tool_call.tool_input_dict,
            result=tool_call.result,
            error=tool_call.error,
        )

    def to_domain(self):
        return ToolCall(
            id=self.id or "",
            tool_name=self.tool_name or "",
            tool_input_dict=self.tool_input_dict or {},
            result=self.result,
            error=self.error,
        )
