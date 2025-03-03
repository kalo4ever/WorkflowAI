from collections.abc import Collection
from typing import AsyncIterator, Literal, NamedTuple, Protocol

from core.domain.review import Review, ReviewerType, ReviewOutcome
from core.domain.run_identifier import RunIdentifier
from core.domain.search_query import ReviewSearchOptions


class AIReviewerFilter(NamedTuple):
    evaluator_id: str | None = None
    input_evaluation_id: str | None = None


class ReviewsStorage(Protocol):
    async def mark_as_stale(
        self,
        task_id: str,
        task_schema_id: int,
        task_input_hash: str,
        task_output_hash: str,
        reviewer_type: ReviewerType,
        before_id: str | None = None,
    ) -> None: ...

    async def insert_review(self, review: Review) -> Review: ...

    # By default only non state reviews are included
    def list_reviews(
        self,
        task_id: str,
        task_schema_id: int,
        task_input_hash: str,
        task_output_hash: str,
        reviewer_type: ReviewerType | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[Review]: ...

    async def get_review_by_id(self, task_id: str, task_schema_id: int, review_id: str) -> Review: ...

    async def get_review_by_hash(
        self,
        task_id: str,
        task_schema_id: int,
        task_input_hash: str,
        task_output_hash: str,
        reviewer: Literal["user", "ai"] | AIReviewerFilter | None = None,
        include: set[Literal["outcome", "status"]] | None = None,
    ) -> Review | None: ...

    # Insert an in progress AI review
    # The call fails if a review with the same properties already exists
    async def insert_in_progress_review(
        self,
        task_id: str,
        task_schema_id: int,
        task_input_hash: str,
        task_output_hash: str,
        # the evaluator_id is optional since we will only have one if we have task level instructions
        evaluator_id: str | None,
        input_evaluation_id: str,
    ) -> Review: ...

    async def complete_review(
        self,
        review_id: str,
        outcome: ReviewOutcome,
        comment: str | None,
        positive_aspects: list[str] | None,
        negative_aspects: list[str] | None,
        confidence_score: float | None,
        run_identifier: RunIdentifier | None,
    ) -> None: ...

    async def fail_review(self, review_id: str) -> None: ...

    async def add_comment_to_review(self, review_id: str, comment: str, responding_to: str) -> None: ...

    async def find_unique_input_hashes(self, task_id: str, task_schema_id: int) -> set[str]: ...

    async def eval_hashes_with_user_reviews(
        self,
        task_id: str,
        task_schema_id: int,
        input_hashes: set[str],
    ) -> set[str]:
        """Return eval hashes that already have a user review"""
        ...

    def reviews_for_eval_hashes(
        self,
        task_id: str,
        eval_hashes: Collection[str],
    ) -> AsyncIterator[Review]: ...

    async def eval_hashes_for_review(
        self,
        task_id: str,
        review: ReviewSearchOptions,
    ) -> set[str]: ...
