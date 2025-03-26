from enum import Enum

from pydantic import BaseModel, Field


class URLStatus(str, Enum):
    REACHABLE = "reachable"
    UNREACHABLE = "unreachable"


class URLContent(BaseModel):
    url: str = Field(description="The URL of the content")
    content: str | None = Field(default=None, description="The content of the URL if reachable")
    status: URLStatus = Field(
        default=URLStatus.REACHABLE,
        description="The status of the URL: reachable or unreachable",
    )
