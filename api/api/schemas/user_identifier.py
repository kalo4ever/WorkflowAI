from pydantic import BaseModel

from core.domain.users import UserIdentifier as DomainUserIdentifier


class UserIdentifier(BaseModel):
    user_id: str | None = None
    user_email: str | None = None

    @classmethod
    def from_domain(cls, user: DomainUserIdentifier | None):
        if not user or (not user.user_id and not user.user_email):
            return None
        return cls(user_id=user.user_id, user_email=user.user_email)
