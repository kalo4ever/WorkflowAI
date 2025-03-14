from typing import Any, AsyncGenerator

from bson import ObjectId

from core.domain.task_evaluator import EvaluatorType, EvaluatorTypeName, TaskEvaluator
from core.storage import TenantTuple
from core.storage.mongo.models.task_evaluator import TaskEvaluatorDocument
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.base_partial_storage import PartialStorage
from core.storage.mongo.utils import dump_model


class MongoEvaluatorStorage(PartialStorage[TaskEvaluatorDocument]):
    def __init__(self, tenant: TenantTuple, collection: AsyncCollection):
        super().__init__(tenant, collection, TaskEvaluatorDocument)

    async def add_task_evaluator(
        self,
        task_id: str,
        task_schema_id: int,
        task_evaluator: TaskEvaluator,
    ) -> TaskEvaluator:
        doc = TaskEvaluatorDocument.from_domain(
            tenant=self._tenant,
            task_id=task_id,
            task_schema_id=task_schema_id,
            evaluator=task_evaluator,
        )
        res = await self._insert_one(doc)
        return res.to_domain()

    def _types_filter(self, types: set[EvaluatorTypeName]):
        if len(types) == 1:
            return next(iter(types))
        return {"$in": list(types)}

    async def list_task_evaluators(
        self,
        task_id: str,
        task_schema_id: int,
        types: set[EvaluatorTypeName] | None = None,
        active: bool | None = True,
        limit: int | None = None,
    ) -> AsyncGenerator[TaskEvaluator, None]:
        filter: dict[str, Any] = {"task_id": task_id, "task_schema_id": task_schema_id}
        if active is not None:
            filter["active"] = active
        if types:
            filter["evaluator_type"] = self._types_filter(types)
        # TODO: test, the sort is not indexed so it might not be super efficient
        async for doc in self._find(filter, limit=limit, sort=[("_id", -1)]):
            yield doc.to_domain()

    def _evaluator_by_id_filter(self, task_id: str, task_schema_id: int, evaluator_id: str) -> dict[str, Any]:
        return {
            "task_id": task_id,
            "task_schema_id": task_schema_id,
            **self._id_filter(evaluator_id),
        }

    async def get_task_evaluator(self, task_id: str, task_schema_id: int, evaluator_id: str) -> TaskEvaluator:
        filter = self._evaluator_by_id_filter(task_id, task_schema_id, evaluator_id)
        doc = await self._find_one(filter)
        return doc.to_domain()

    async def set_task_evaluator_active(
        self,
        task_id: str,
        task_schema_id: int,
        evaluator_id: str,
        active: bool,
    ) -> None:
        filter = self._evaluator_by_id_filter(task_id, task_schema_id, evaluator_id)
        await self._update_one(filter, {"$set": {"active": active}})

    async def patch_evaluator(
        self,
        id: str,
        active: bool,
        is_loading: bool,
        evaluator_type: EvaluatorType,
    ):
        filter = self._id_filter(id)
        update: dict[str, Any] = {
            "$set": {
                "active": active,
                "properties": dump_model(TaskEvaluatorDocument.Properties.from_domain(evaluator_type)),
            },
        }

        if not is_loading:
            update["$unset"] = {"is_loading": ""}
        else:
            update["$set"]["is_loading"] = is_loading

        await self._update_one(filter, update)

    async def deactivate_evaluators(
        self,
        task_id: str,
        task_schema_id: int,
        except_id: str | None,
        types: set[EvaluatorTypeName] | None,
    ) -> None:
        filter: dict[str, Any] = {
            "task_id": task_id,
            "task_schema_id": task_schema_id,
            "active": True,
        }
        if types:
            filter["evaluator_type"] = self._types_filter(types)
        if except_id:
            filter["_id"] = {"$ne": ObjectId(except_id)}
        await self._update_many(filter, {"$set": {"active": False}})
