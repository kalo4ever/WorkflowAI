from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

from core.domain.run_identifier import RunIdentifier
from core.domain.users import UserIdentifier
from core.domain.utils import compute_eval_hash

ReviewerType = Literal["user", "ai"]
ReviewOutcome = Literal["positive", "negative", "unsure"]


class Review(BaseModel):
    id: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.min)
    task_id: str
    task_uid: int = 0  # TODO: make it mandatory
    task_schema_id: int

    task_input_hash: str
    task_output_hash: str
    eval_hash: str = ""
    outcome: ReviewOutcome | None
    status: Literal["in_progress", "completed"]

    comment: str | None = None

    positive_aspects: list[str] | None = None
    negative_aspects: list[str] | None = None

    is_stale: bool = False

    class UserReviewer(UserIdentifier):
        reviewer_type: Literal["user"] = "user"

    class AIReviewer(BaseModel):
        reviewer_type: Literal["ai"] = "ai"
        evaluator_id: str | None = None
        input_evaluation_id: str = ""

        confidence_score: float | None = None
        run_identifier: RunIdentifier | None = None

    reviewer: Annotated[UserReviewer | AIReviewer, Field(discriminator="reviewer_type")]

    responding_to_review_id: str | None = None

    @model_validator(mode="after")
    def compute_eval_hash(self):
        if not self.eval_hash:
            self.eval_hash = compute_eval_hash(self.task_schema_id, self.task_input_hash, self.task_output_hash)
        return self
