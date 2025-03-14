from datetime import datetime

from pydantic import BaseModel

from core.domain.users import UserIdentifier


class APIKey(BaseModel):
    id: str
    name: str
    partial_key: str
    created_at: datetime
    last_used_at: datetime | None
    created_by: UserIdentifier
