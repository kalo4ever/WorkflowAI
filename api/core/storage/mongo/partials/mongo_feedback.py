from collections.abc import AsyncIterator
from typing import Any, override

from bson import ObjectId

from core.domain.feedback import Feedback, FeedbackAnnotation
from core.storage import TenantTuple
from core.storage.feedback_storage import FeedbackStorage
from core.storage.mongo.models.feedback_document import FeedbackDocument
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.base_partial_storage import PartialStorage
from core.storage.mongo.utils import dump_model


class MongoFeedbackStorage(PartialStorage[FeedbackDocument], FeedbackStorage):
    def __init__(self, tenant: TenantTuple, collection: AsyncCollection):
        super().__init__(tenant, collection, FeedbackDocument)

    @override
    def _tenant_filter(self, filter: dict[str, Any]) -> dict[str, Any]:
        return {**filter, "tenant_uid": self._tenant_uid}

    @override
    async def store_feedback(self, tenant_uid: int, task_uid: int, feedback: Feedback):
        await self._collection.update_one(
            {
                "tenant_uid": tenant_uid,
                "task_uid": task_uid,
                "run_id": feedback.run_id,
                "is_stale": False,
                "user_id": feedback.user_id or "",
            },
            {"$set": {"is_stale": True}},
            hint="unique_by_user_id",
        )
        doc = FeedbackDocument(
            tenant_uid=tenant_uid,
            task_uid=task_uid,
            outcome=feedback.outcome,
            comment=feedback.comment,
            # Inserting an empty user id to
            user_id=feedback.user_id or "",
            run_id=feedback.run_id,
            is_stale=False,
        )
        res = await self._collection.insert_one(dump_model(doc))
        doc.id = res.inserted_id
        return doc.to_domain()

    @override
    async def get_feedback(self, tenant_uid: int, task_uid: int, run_id: str, user_id: str | None) -> Feedback | None:
        doc = await self._collection.find_one(
            {
                "tenant_uid": tenant_uid,
                "task_uid": task_uid,
                "run_id": run_id,
                "user_id": user_id or "",
                "is_stale": False,
            },
            projection={"outcome": 1, "comment": 1},
        )
        return FeedbackDocument.model_validate(doc).to_domain() if doc else None

    @override
    async def add_annotation(self, feedback_id: str, annotation: FeedbackAnnotation):
        await self._update_one(
            {"_id": ObjectId(feedback_id)},
            {"$push": {"annotations": dump_model(FeedbackDocument.Annotation.from_domain(annotation))}},
        )

    def _feedback_filter(self, task_uid: int, run_id: str | None) -> dict[str, Any]:
        filter: dict[str, Any] = {"task_uid": task_uid, "is_stale": False}
        if run_id:
            filter["run_id"] = run_id
        return filter

    @override
    async def list_feedback(
        self,
        task_uid: int,
        run_id: str | None,
        limit: int = 30,
        offset: int = 0,
    ) -> AsyncIterator[Feedback]:
        filter = self._feedback_filter(task_uid, run_id)
        async for doc in self._find(filter, sort=[("_id", -1)], limit=limit, skip=offset):
            yield doc.to_domain()

    @override
    async def count_feedback(self, task_uid: int, run_id: str | None) -> int:
        return await self._count(self._feedback_filter(task_uid, run_id))
