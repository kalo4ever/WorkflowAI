from typing import Any

from pydantic import Field

from core.utils.models.hashable import HashableModel


class Tool(HashableModel):
    name: str = Field(description="The name of the tool")
    description: str = Field(default="", description="The description of the tool")

    input_schema: dict[str, Any] = Field(description="The input class of the tool")
    output_schema: dict[str, Any] = Field(description="The output class of the tool")
