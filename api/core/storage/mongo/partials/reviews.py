from collections.abc import Collection
from typing import Any, AsyncIterator, Literal

from bson import ObjectId
from bson.errors import InvalidId

from core.domain.errors import DefaultError
from core.domain.review import Review, ReviewerType, ReviewOutcome
from core.domain.run_identifier import RunIdentifier
from core.domain.search_query import ReviewSearchOptions
from core.storage import ObjectNotFoundException, TenantTuple
from core.storage.mongo.models.pyobjectid import PyObjectID
from core.storage.mongo.models.review_document import ReviewDocument
from core.storage.mongo.models.run_identifier import RunIdentifier as RunIdentifierSchema
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.base_partial_storage import PartialStorage
from core.storage.mongo.utils import dump_model, projection, query_set_filter
from core.storage.reviews_storage import AIReviewerFilter


class MongoReviewsStorage(PartialStorage[ReviewDocument]):
    def __init__(self, tenant: TenantTuple, collection: AsyncCollection):
        super().__init__(tenant, collection, ReviewDocument)

    async def mark_as_stale(
        self,
        task_id: str,
        task_schema_id: int,
        task_input_hash: str,
        task_output_hash: str,
        reviewer_type: ReviewerType,
        before_id: str | None = None,
    ):
        filter: dict[str, Any] = {
            "task_id": task_id,
            "task_schema_id": task_schema_id,
            "task_input_hash": task_input_hash,
            "task_output_hash": task_output_hash,
            "reviewer.reviewer_type": reviewer_type,
            "is_stale": False,
        }
        if before_id:
            filter["_id"] = {"$lt": ObjectId(before_id)}

        await self._update_many(
            filter=filter,
            update={"$set": {"is_stale": True}},
            hint="reviews_non_stale_index",
        )

    async def insert_review(self, review: Review) -> Review:
        review_doc = ReviewDocument.from_domain(review)
        await self._insert_one(review_doc)
        return review_doc.to_domain()

    async def list_reviews(
        self,
        task_id: str,
        task_schema_id: int,
        task_input_hash: str,
        task_output_hash: str,
        reviewer_type: ReviewerType | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[Review]:
        filter = {
            "task_id": task_id,
            "task_schema_id": task_schema_id,
            "task_input_hash": task_input_hash,
            "task_output_hash": task_output_hash,
            "is_stale": False,
        }
        if reviewer_type:
            filter["reviewer.reviewer_type"] = reviewer_type

        async for doc in self._find(filter=filter, limit=limit, sort=[("_id", -1)], hint="reviews_non_stale_index"):
            yield doc.to_domain()

    async def get_review_by_id(self, task_id: str, task_schema_id: int, review_id: str) -> Review:
        try:
            obj_id = ObjectId(review_id)
        except InvalidId:
            raise DefaultError(f"Invalid review ID: {review_id}", status_code=400, code="bad_request")

        doc = await self._find_one(
            filter={"task_id": task_id, "task_schema_id": task_schema_id, "_id": obj_id},
        )
        return doc.to_domain()

    async def get_review_by_hash(
        self,
        task_id: str,
        task_schema_id: int,
        task_input_hash: str,
        task_output_hash: str,
        reviewer: Literal["user", "ai"] | AIReviewerFilter | None = None,
        include: set[Literal["outcome", "status"]] | None = None,
    ) -> Review | None:
        filter = {
            "task_id": task_id,
            "task_schema_id": task_schema_id,
            "task_input_hash": task_input_hash,
            "task_output_hash": task_output_hash,
            "is_stale": False,
        }
        if reviewer == "user":
            filter["reviewer.reviewer_type"] = "user"
        elif reviewer == "ai":
            filter["reviewer.reviewer_type"] = "ai"
        elif isinstance(reviewer, AIReviewerFilter):
            filter["reviewer.reviewer_type"] = "ai"
            if reviewer.evaluator_id is not None:
                filter["reviewer.evaluator_id"] = reviewer.evaluator_id
            if reviewer.input_evaluation_id is not None:
                filter["reviewer.input_evaluation_id"] = reviewer.input_evaluation_id

        try:
            doc = await self._find_one(
                filter=filter,
                projection=projection(include=include),
                hint="reviews_non_stale_index",
            )
            return doc.to_domain() if doc else None
        except ObjectNotFoundException:
            return None

    async def insert_in_progress_review(
        self,
        task_id: str,
        task_schema_id: int,
        task_input_hash: str,
        task_output_hash: str,
        evaluator_id: str | None,
        input_evaluation_id: str,
    ) -> Review:
        review = ReviewDocument(
            task_id=task_id,
            task_schema_id=task_schema_id,
            task_input_hash=task_input_hash,
            task_output_hash=task_output_hash,
            status="in_progress",
            reviewer=ReviewDocument.AIReviewer(evaluator_id=evaluator_id, input_evaluation_id=input_evaluation_id),
            outcome=None,
        )

        result = await self._insert_one(review)
        return result.to_domain()

    async def complete_review(
        self,
        review_id: str,
        outcome: ReviewOutcome,
        comment: str | None = None,
        positive_aspects: list[str] | None = None,
        negative_aspects: list[str] | None = None,
        confidence_score: float | None = None,
        run_identifier: RunIdentifier | None = None,
    ):
        await self._update_one(
            filter={"_id": ObjectId(review_id), "status": "in_progress"},
            update={
                "$set": {
                    "outcome": outcome,
                    "comment": comment,
                    "positive_aspects": positive_aspects,
                    "negative_aspects": negative_aspects,
                    "reviewer.confidence_score": confidence_score,
                    "reviewer.run_identifier": dump_model(RunIdentifierSchema.from_domain(run_identifier))
                    if run_identifier
                    else None,
                    "status": "completed",
                },
            },
        )

    async def fail_review(self, review_id: str):
        await self._delete_one(filter={"_id": ObjectId(review_id), "status": "in_progress"})

    async def add_comment_to_review(self, review_id: str, comment: str, responding_to: str | None = None):
        update = {"comment": comment}
        if responding_to_id := PyObjectID.cast(responding_to):
            update["in_response_to"] = responding_to_id

        await self._update_one(
            filter={"_id": ObjectId(review_id), "reviewer.reviewer_type": "user"},
            update={"$set": update},
        )

    async def find_unique_input_hashes(self, task_id: str, task_schema_id: int) -> set[str]:
        return await self._distinct(
            key="task_input_hash",
            filter=self._tenant_filter({"task_id": task_id, "task_schema_id": task_schema_id, "is_stale": False}),
            hint="reviews_non_stale_index",
        )

    async def eval_hashes_for_review(self, task_id: str, review: ReviewSearchOptions):
        filter = {
            "task_id": task_id,
            "is_stale": False,
        }
        match review:
            case ReviewSearchOptions.POSITIVE:
                filter["outcome"] = "positive"
            case ReviewSearchOptions.NEGATIVE:
                filter["outcome"] = "negative"
            case ReviewSearchOptions.UNSURE:
                filter["outcome"] = "unsure"
            case ReviewSearchOptions.ANY:
                pass

        return await self._distinct(key="eval_hash", filter=filter, hint="outcome_to_eval_hash")

    async def eval_hashes_with_user_reviews(
        self,
        task_id: str,
        task_schema_id: int,
        input_hashes: set[str],
    ) -> set[str]:
        return {
            r.eval_hash
            async for r in self._find(
                filter={
                    "task_id": task_id,
                    "task_schema_id": task_schema_id,
                    "task_input_hash": query_set_filter(input_hashes, inc=True),
                    "reviewer.reviewer_type": "user",
                    "is_stale": False,
                },
                projection={"eval_hash": 1},
                hint="reviews_non_stale_index",
            )
        }

    async def reviews_for_eval_hashes(
        self,
        task_id: str,
        eval_hashes: Collection[str],
    ) -> AsyncIterator[Review]:
        filter = {
            "task_id": task_id,
            "eval_hash": query_set_filter(eval_hashes, inc=True),
            "is_stale": False,
        }
        async for doc in self._find(filter, hint="eval_hash"):
            yield doc.to_domain()
