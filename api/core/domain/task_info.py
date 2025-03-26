from typing import Any

from pydantic import BaseModel

from core.domain.ban import Ban
from core.storage import TaskTuple


class PublicTaskInfo(BaseModel):
    uid: int = 0
    task_id: str
    name: str = ""
    is_public: bool = False
    # TODO[uids]: remove once we don't need the string tenant anymore
    tenant: str = ""
    tenant_uid: int = 0


class TaskInfo(BaseModel):
    uid: int = 0
    task_id: str
    name: str = ""
    description: str | None = None
    is_public: bool = False
    hidden_schema_ids: list[int] | None = None
    schema_details: list[dict[str, Any]] | None = None
    ban: Ban | None = None

    def get_schema_details(self, schema_id: int) -> dict[str, Any] | None:
        try:
            return next(detail for detail in self.schema_details or [] if detail["schema_id"] == schema_id)
        except StopIteration:
            return None

    @property
    def id_tuple(self) -> TaskTuple:
        return (self.task_id, self.uid)
