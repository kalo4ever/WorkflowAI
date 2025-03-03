from typing import AsyncIterator, Protocol

from api.dependencies.path_params import TaskID, TaskSchemaID
from core.domain.changelogs import VersionChangelog


class ChangeLogStorage(Protocol):
    async def insert_changelog(self, changelog: VersionChangelog) -> VersionChangelog: ...

    def list_changelogs(
        self,
        task_id: TaskID,
        task_schema_id: TaskSchemaID | None,
    ) -> AsyncIterator[VersionChangelog]: ...
