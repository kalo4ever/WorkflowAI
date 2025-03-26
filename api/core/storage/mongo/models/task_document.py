from typing import Any

from pydantic import Field

from core.domain.task_info import PublicTaskInfo, TaskInfo
from core.storage.mongo.models.base_document import BaseDocumentWithID
from core.storage.mongo.models.task_ban import BanDocument
from core.utils.ids import id_uint32


class TaskDocument(BaseDocumentWithID):
    uid: int = Field(default_factory=id_uint32)
    task_id: str
    is_public: bool = False
    name: str = ""
    description: str | None = None
    hidden_schema_ids: list[int] | None = None
    schema_details: list[dict[str, Any]] | None = None
    ban: BanDocument | None = None

    def to_domain(self) -> TaskInfo:
        return TaskInfo(
            uid=self.uid,
            task_id=self.task_id,
            name=self.name,
            is_public=self.is_public,
            description=self.description,
            hidden_schema_ids=self.hidden_schema_ids,
            schema_details=self.schema_details,
            ban=self.ban.to_domain() if self.ban else None,
        )

    def to_public_domain(self) -> PublicTaskInfo:
        return PublicTaskInfo(
            uid=self.uid,
            task_id=self.task_id,
            name=self.name,
            is_public=self.is_public,
            tenant=self.tenant or "",
            tenant_uid=self.tenant_uid or 0,
        )
