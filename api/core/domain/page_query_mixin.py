from typing import Optional

from pydantic import BaseModel, Field


class PageQueryMixin(BaseModel):
    limit: Optional[int] = Field(default=None, description="The number of items to return")
    offset: Optional[int] = Field(default=None, description="The number of items to skip")
