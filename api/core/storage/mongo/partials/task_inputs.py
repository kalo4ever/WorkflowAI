import asyncio
from collections.abc import AsyncIterator, Iterable
from typing import Any

from pymongo.errors import BulkWriteError, DuplicateKeyError

from core.domain.task_input import TaskInput, TaskInputFields, TaskInputQuery
from core.domain.task_variant import SerializableTaskVariant
from core.storage import TenantTuple
from core.storage.mongo.models.task_input import TaskInputDocument
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.base_partial_storage import PartialStorage
from core.storage.mongo.utils import projection


class MongoTaskInputStorage(PartialStorage[TaskInputDocument]):
    def __init__(self, tenant: TenantTuple, collection: AsyncCollection):
        super().__init__(tenant, collection, TaskInputDocument)

    def _by_hash_filter(self, task_id: str, task_schema_id: int, input_hash: str) -> dict[str, Any]:
        return {"task.id": task_id, "task.schema_id": task_schema_id, "task_input_hash": input_hash}

    async def get_input_by_hash(
        self,
        task_id: str,
        task_schema_id: int,
        input_hash: str,
        exclude: Iterable[TaskInputFields] | None = None,
    ) -> TaskInput:
        doc = await self._find_one(
            self._by_hash_filter(task_id, task_schema_id, input_hash),
            projection=projection(exclude=exclude),
        )
        return doc.to_domain()

    async def _patch_datasets_and_example(self, task_input: TaskInputDocument):
        if not task_input.task:
            raise ValueError("Task input must have a task")
        update: dict[str, Any] = {}
        if task_input.datasets:
            update["$addToSet"] = {"datasets": {"$each": task_input.datasets}}
        if task_input.example_id:
            update["$set"] = {"example_id": task_input.example_id, "example_preview": task_input.example_preview}
        res = await self._update_one(
            self._by_hash_filter(task_input.task.id, task_input.task.schema_id, task_input.task_input_hash),
            update,
        )
        if res.matched_count == 0:
            self._logger.error(
                "Failed to add datasets to existing input",
                extra={"task_input": task_input.model_dump()},
            )

    async def create_inputs(self, task: SerializableTaskVariant, task_inputs: Iterable[TaskInput]):
        docs = [TaskInputDocument.from_domain(task, i) for i in task_inputs]
        try:
            await self.insert_many(docs, ordered=False)
        except BulkWriteError as e:
            errs = e.details["writeErrors"]
            if not errs:
                raise e

            docs_to_patch: list[TaskInputDocument] = []
            # Checking that all errors are duplicate keys which would be fine
            for err in errs:
                if err["code"] != 11000:
                    raise e
                idx: int = err["index"]
                doc = docs[idx]
                if doc.datasets:
                    docs_to_patch.append(doc)

            await asyncio.gather(*(self._patch_datasets_and_example(doc) for doc in docs_to_patch))

    async def create_input(self, task: SerializableTaskVariant, task_input: TaskInput) -> TaskInput:
        task_input_schema = TaskInputDocument.from_domain(task, task_input)
        try:
            await self._insert_one(task_input_schema)
        except DuplicateKeyError:
            # making sure that the existing input has the datasets included in the request
            if task_input_schema.datasets:
                doc = await self._find_one_and_update(
                    self._by_hash_filter(task.task_id, task.task_schema_id, task_input.task_input_hash),
                    {"$addToSet": {"datasets": {"$each": task_input_schema.datasets}}},
                    return_document=True,
                )
                return doc.to_domain()

            return await self.get_input_by_hash(task.task_id, task.task_schema_id, task_input.task_input_hash)

        return task_input

    async def attach_example(
        self,
        task_id: str,
        task_schema_id: int,
        input_hash: str,
        example_id: str,
        example_preview: str,
    ):
        await self._update_one(
            self._by_hash_filter(task_id, task_schema_id, input_hash),
            {"$set": {"example_id": example_id, "example_preview": example_preview}},
        )

    async def detach_example(self, task_id: str, task_schema_id: int, input_hash: str, example_id: str):
        await self._update_one(
            {**self._by_hash_filter(task_id, task_schema_id, input_hash), "example_id": example_id},
            {"$unset": {"example_id": "", "example_preview": ""}},
        )

    async def remove_inputs_from_datasets(
        self,
        task_id: str,
        task_schema_id: int,
        dataset_id: str,
        input_hashes: list[str],
    ):
        await self._update_many(
            {
                "task.id": task_id,
                "task.schema_id": task_schema_id,
                "datasets": dataset_id,
                "task_input_hash": {"$in": input_hashes},
            },
            {"$pull": {"datasets": dataset_id}},
        )

    async def list_inputs(self, query: TaskInputQuery) -> AsyncIterator[TaskInput]:
        filter = TaskInputDocument.build_filter(self._tenant, query)
        project = TaskInputDocument.build_project(query)
        res = self._find(filter, projection=project, limit=query.limit, skip=query.offset)
        async for doc in res:
            yield doc.to_domain()

    async def count_inputs(self, query: TaskInputQuery) -> tuple[int, int]:
        filter = TaskInputDocument.build_filter(self._tenant, query)
        pipeline = [
            {"$match": filter},
            {
                "$facet": {
                    "total_count": [{"$count": "count"}],
                    "existing_field_count": [{"$match": {"example_id": {"$exists": True}}}, {"$count": "count"}],
                },
            },
        ]

        result = await anext(self._collection.aggregate(pipeline))
        total_count = result["total_count"][0]["count"] if result["total_count"] else 0
        existing_field_count = result["existing_field_count"][0]["count"] if result["existing_field_count"] else 0

        return total_count, existing_field_count
