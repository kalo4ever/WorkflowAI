from datetime import datetime

from pydantic import BaseModel, Field

from core.domain.task_info import PublicTaskInfo, TaskInfo
from core.storage.mongo.models.base_document import BaseDocumentWithID
from core.storage.mongo.models.task_ban import BanDocument
from core.utils.ids import id_uint32
from core.utils.iter_utils import safe_map_optional


class TaskDocument(BaseDocumentWithID):
    uid: int = Field(default_factory=id_uint32)
    task_id: str
    is_public: bool = False
    name: str = ""
    description: str | None = None
    hidden_schema_ids: list[int] | None = None

    class SchemaDetails(BaseModel):
        schema_id: int = 0
        last_active_at: datetime | None = None

        def to_domain(self) -> TaskInfo.SchemaDetails:
            return TaskInfo.SchemaDetails(
                schema_id=self.schema_id,
                last_active_at=self.last_active_at,
            )

    schema_details: list[SchemaDetails] | None = None
    ban: BanDocument | None = None

    def to_domain(self) -> TaskInfo:
        return TaskInfo(
            uid=self.uid,
            task_id=self.task_id,
            name=self.name,
            is_public=self.is_public,
            description=self.description,
            hidden_schema_ids=self.hidden_schema_ids,
            schema_details=safe_map_optional(self.schema_details, self.SchemaDetails.to_domain),
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
