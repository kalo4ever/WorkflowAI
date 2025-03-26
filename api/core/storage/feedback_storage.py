from collections.abc import AsyncIterator
from typing import Protocol

from core.domain.feedback import Feedback, FeedbackAnnotation


class FeedbackSystemStorage(Protocol):
    async def store_feedback(self, tenant_uid: int, task_uid: int, feedback: Feedback) -> Feedback: ...
    async def get_feedback(
        self,
        tenant_uid: int,
        task_uid: int,
        run_id: str,
        user_id: str | None,
    ) -> Feedback | None: ...


class FeedbackStorage(FeedbackSystemStorage):
    async def add_annotation(self, feedback_id: str, annotation: FeedbackAnnotation) -> None: ...

    def list_feedback(
        self,
        task_uid: int,
        run_id: str | None,
        limit: int,
        offset: int,
    ) -> AsyncIterator[Feedback]: ...

    async def count_feedback(self, task_uid: int, run_id: str | None) -> int: ...
