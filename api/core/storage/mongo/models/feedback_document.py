from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from core.domain.feedback import Feedback, FeedbackAnnotation
from core.domain.users import UserIdentifier
from core.storage.mongo.models.base_document import BaseDocumentWithID
from core.storage.mongo.models.user_identifier import UserIdentifierSchema


class FeedbackDocument(BaseDocumentWithID):
    task_uid: int = 0
    run_id: str = ""
    outcome: Literal["positive", "negative"]
    comment: str | None = None
    # User_id is empty for anonymous users, this allows easy queries
    user_id: str = ""

    class Annotation(BaseModel):
        status: Literal["resolved", "incorrect", "correct"]
        comment: str | None
        annotated_by: UserIdentifierSchema | None = None
        created_at: datetime

        def to_domain(self):
            return FeedbackAnnotation(
                status=self.status,
                comment=self.comment,
                annotated_by=self.annotated_by.to_domain() if self.annotated_by else UserIdentifier(),
            )

        @classmethod
        def from_domain(cls, annotation: FeedbackAnnotation):
            return cls(
                status=annotation.status,
                comment=annotation.comment,
                annotated_by=UserIdentifierSchema.from_domain(annotation.annotated_by),
                created_at=annotation.created_at or datetime.now(),
            )

    annotations: list[Annotation] | None = None
    is_stale: bool = False

    def to_domain(self):
        return Feedback(
            run_id=self.run_id,
            outcome=self.outcome,
            comment=self.comment,
            user_id=self.user_id or None,
            annotation=self.annotations[-1].to_domain() if self.annotations else None,
            created_at=self.id.generation_time if self.id else None,
            id=str(self.id) if self.id else "",
        )
