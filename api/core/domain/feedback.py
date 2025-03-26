from datetime import datetime
from typing import Literal, NamedTuple, TypeAlias

from core.domain.users import UserIdentifier

FeedbackOutcome: TypeAlias = Literal["positive", "negative"]
FeedbackAnnotationStatus: TypeAlias = Literal["resolved", "incorrect", "correct"]


class FeedbackAnnotation(NamedTuple):
    status: FeedbackAnnotationStatus
    comment: str | None
    annotated_by: UserIdentifier
    created_at: datetime | None = None


class Feedback(NamedTuple):
    """A final user feedback on a run"""

    run_id: str
    outcome: FeedbackOutcome
    comment: str | None
    user_id: str | None

    id: str = ""
    created_at: datetime | None = None
    annotation: FeedbackAnnotation | None = None
