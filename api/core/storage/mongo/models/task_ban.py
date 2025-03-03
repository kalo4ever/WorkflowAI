from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from core.domain.ban import Ban


class BanDocument(BaseModel):
    banned_at: datetime
    reason: Literal["task_run_non_compliant", "task_version_non_compliant"]
    related_ids: list[str]  # The ids of the runs, versions, etc that triggered the ban

    def to_domain(self) -> Ban:
        return Ban(
            banned_at=self.banned_at,
            reason=self.reason,
            related_ids=self.related_ids,
        )
