import logging
from typing import Any, Self

from pydantic import BaseModel, ValidationError

from core.domain.users import UserIdentifier


class UserIdentifierSchema(BaseModel):
    user_id: str | None = None
    user_email: str | None = None

    def to_domain(self) -> UserIdentifier:
        return UserIdentifier(
            user_id=self.user_id,
            user_email=self.user_email,
        )

    @classmethod
    def from_domain(cls, user: UserIdentifier) -> Self:
        return cls(
            user_id=user.user_id,
            user_email=user.user_email,
        )

    @classmethod
    def to_domain_optional(cls, doc: dict[str, Any]) -> UserIdentifier | None:
        if not doc:
            return None
        try:
            return UserIdentifierSchema.model_validate(doc).to_domain()
        except ValidationError:
            logging.getLogger(__name__).exception("Invalid user identifier", extra={"doc": doc})
            return None
