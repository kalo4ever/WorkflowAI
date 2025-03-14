from typing import Any

from pydantic import BaseModel, Field

from core.domain.tool_call import ToolCallRequestWithID


class APIToolCallRequest(BaseModel):
    id: str = Field(description="The id of the tool use. The id should be used when returning the result.")
    name: str = Field(description="The name of the tool")
    input: dict[str, Any] = Field(description="The input tool should be executed with")

    @classmethod
    def from_domain(cls, tool_call: ToolCallRequestWithID):
        return cls(id=tool_call.id, name=tool_call.tool_name, input=tool_call.tool_input_dict)
