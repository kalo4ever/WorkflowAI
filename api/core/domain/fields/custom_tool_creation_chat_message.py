from typing import Any, Literal

from pydantic import BaseModel, Field


class CustomToolCreationChatMessage(BaseModel):
    role: Literal["USER", "ASSISTANT"] | None = Field(
        default=None,
        description="The role of the message sender",
    )
    content: str | None = Field(
        default=None,
        description="The content of the message",
    )

    class Tool(BaseModel):
        name: str | None = Field(
            default=None,
            description="The name of the tool",
        )
        description: str | None = Field(
            default=None,
            description="The description of the tool",
        )
        parameters: dict[str, Any] | None = Field(
            default=None,
            description="The parameters of the tool in JSON Schema format",
        )

    tool: Tool | None = Field(
        default=None,
        description="The proposed tool to create",
    )
