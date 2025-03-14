import logging
from typing import Self

from core.domain.changelogs import VersionChangelog
from core.storage.mongo.models.base_document import BaseDocumentWithID

_logger = logging.getLogger(__name__)


class ChangeLogDocument(BaseDocumentWithID):
    task_id: str
    task_schema_id: int
    # Old changelogs did not have a minor version
    major_from: int | None = None
    major_to: int | None = None

    similarity_hash_from: str = ""
    similarity_hash_to: str = ""

    changelog: list[str] | None = None

    @classmethod
    def from_domain(cls, changelog: VersionChangelog) -> Self:
        return cls(
            task_id=changelog.task_id,
            task_schema_id=changelog.task_schema_id,
            major_from=changelog.major_from,
            major_to=changelog.major_to,
            similarity_hash_from=changelog.similarity_hash_from,
            similarity_hash_to=changelog.similarity_hash_to,
            changelog=changelog.changelog,
        )

    def to_domain(self) -> VersionChangelog:
        return VersionChangelog(
            task_id=self.task_id,
            task_schema_id=self.task_schema_id,
            # Just in case, for backwards compatibility
            major_from=self.major_from or 0,
            major_to=self.major_to or 0,
            similarity_hash_from=self.similarity_hash_from,
            similarity_hash_to=self.similarity_hash_to,
            changelog=self.changelog or [],
        )
