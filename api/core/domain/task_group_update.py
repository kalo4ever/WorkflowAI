from datetime import datetime
from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator


class TaskGroupUpdate(BaseModel):
    """Model representing an update to a task group."""

    is_favorite: bool | None = Field(
        default=None,
        strict=True,  # Ensure strict boolean validation
        description="Set to True to mark the group as a favorite, False to unmark it, or None to leave it unchanged.",
    )

    notes: str | None = Field(
        default=None,
        description="Additional notes or comments about the task group. Set to None to leave unchanged.",
    )

    last_active_at: datetime | None = Field(
        default=None,
        description="The last time the task group was active.",
    )

    @field_validator("notes")
    @classmethod
    def check_notes(cls, value: str | None) -> str | None:
        if value is not None and value.strip() == "" and value != "":
            raise ValueError("Notes cannot be whitespace-only strings")
        return value

    @model_validator(mode="after")
    def post_validate(self) -> Self:
        """Post-validation to ensure at least one field is set and no conflicting or empty aliases."""
        if not self.model_dump(exclude_none=True):
            raise ValueError("At least one of is_favorite, or notes must be set")
        return self
