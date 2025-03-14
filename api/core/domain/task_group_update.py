import logging
from datetime import datetime
from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator

_logger = logging.getLogger(__name__)


class TaskGroupUpdate(BaseModel):
    """Model representing an update to a task group."""

    add_alias: str | None = Field(
        default=None,
        description=(
            "A new alias for the group. If the alias is already used in another group of the task schema, "
            "it will be removed from the other group."
        ),
        deprecated=True,
    )
    remove_alias: str | None = Field(
        default=None,
        description="An alias to remove from the group. The request is a noop if the group does not have the alias.",
        deprecated=True,
    )
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

    @field_validator("add_alias", "remove_alias")
    @classmethod
    def check_empty_alias(cls, value: str | None) -> str | None:
        if value == "":
            raise ValueError("Aliases cannot be empty strings")
        return value

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
        if self.add_alias or self.remove_alias:
            _logger.error(
                "Updating a group alias is deprecated",
                extra={"add_alias": self.add_alias, "remove_alias": self.remove_alias},
            )
            raise ValueError("Updating a group alias is deprecated")
        return self
