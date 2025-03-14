import pymongo
from bson import ObjectId

from core.domain.input_evaluation import InputEvaluation
from core.storage import ObjectNotFoundException, TenantTuple
from core.storage.mongo.models.input_evaluation_document import InputEvaluationDocument
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.base_partial_storage import PartialStorage


class MongoInputEvaluationStorage(PartialStorage[InputEvaluationDocument]):
    def __init__(self, tenant: TenantTuple, collection: AsyncCollection):
        super().__init__(tenant, collection, InputEvaluationDocument)

    async def get_latest_input_evaluation(
        self,
        task_id: str,
        task_schema_id: int,
        input_hash: str,
    ) -> InputEvaluation | None:
        try:
            doc = await self._find_one(
                {
                    "task_id": task_id,
                    "task_schema_id": task_schema_id,
                    "task_input_hash": input_hash,
                },
                sort=[("_id", pymongo.DESCENDING)],
            )
            return doc.to_domain()
        except ObjectNotFoundException:
            return None

    # TODO: test
    async def create_input_evaluation(
        self,
        task_id: str,
        task_schema_id: int,
        input_evaluation: InputEvaluation,
    ) -> InputEvaluation:
        doc = InputEvaluationDocument.from_domain(task_id, task_schema_id, input_evaluation)
        return (await self._insert_one(doc)).to_domain()

    async def get_input_evaluation(
        self,
        task_id: str,
        task_schema_id: int,
        input_evaluation_id: str,
    ) -> InputEvaluation:
        doc = await self._find_one(
            {"_id": ObjectId(input_evaluation_id), "task_id": task_id, "task_schema_id": task_schema_id},
        )
        return doc.to_domain()

    async def list_input_evaluations_unique_by_hash(
        self,
        task_id: str,
        task_schema_id: int,
    ):
        # This will scan every document for a given task_id and task_schema_id
        # which is not great but we should not have too many of them
        pipeline = [
            {"$match": self._tenant_filter({"task_id": task_id, "task_schema_id": task_schema_id})},
            {"$sort": {"_id": pymongo.DESCENDING}},
            {"$group": {"_id": "$task_input_hash", "doc": {"$first": "$$ROOT"}}},
        ]
        cursor = self._collection.aggregate(pipeline)
        async for doc in cursor:
            doc = InputEvaluationDocument.model_validate(doc["doc"])
            yield doc.to_domain()

    async def unique_input_hashes(self, task_id: str, task_schema_id: int):
        return await self._distinct(
            "task_input_hash",
            {"task_id": task_id, "task_schema_id": task_schema_id},
            hint="fetch_latest_input_evaluation",
        )
