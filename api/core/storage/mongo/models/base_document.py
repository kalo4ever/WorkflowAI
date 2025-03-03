from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from core.storage.mongo.models.pyobjectid import PyObjectID
from core.utils.fields import datetime_factory


class BaseDocument(BaseModel):
    # Default is provided for when projections are used
    tenant: str = Field(default="", description="The tenant this document belongs to")
    # This field is mostly not used yet, but ultimately it should replace the tenant field
    tenant_uid: int | None = Field(default=None, description="The tenant UID this document belongs to")


class BaseDocumentWithID(BaseDocument):
    id: Optional[PyObjectID] = Field(default=None, alias="_id")

    @property
    def generation_time(self) -> datetime:
        return self.id.generation_time if self.id else datetime_factory()


class BaseDocumentWithStrID(BaseDocument):
    id: str = Field(alias="_id", default="")


class TaskIdAndSchemaMixin(BaseModel):
    task_id: str = ""
    task_schema_id: int = 0
    task_uid: int = 0
