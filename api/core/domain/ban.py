from datetime import datetime

from pydantic import BaseModel
from typing_extensions import Literal


class Ban(BaseModel):
    banned_at: datetime
    reason: Literal["task_run_non_compliant", "task_version_non_compliant"]
    related_ids: list[str]  # The ids of the runs, versions, etc that triggered the ban
