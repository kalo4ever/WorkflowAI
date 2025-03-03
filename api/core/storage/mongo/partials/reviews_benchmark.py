from collections.abc import Iterable
from datetime import datetime
from typing import Any

from core.domain.errors import BadRequestError
from core.domain.task_group_properties import TaskGroupProperties
from core.storage import ObjectNotFoundException, TenantTuple
from core.storage.mongo.models.task_review_benchmarks import TaskReviewBenchmarkDocument
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.base_partial_storage import PartialStorage
from core.storage.mongo.utils import dump_model
from core.storage.review_benchmark_storage import RunReviewAggregateWithIteration

_BY_TASK_SCHEMA_UNIQUE = "by_task_schema_unique"


class MongoReviewsBenchmarkStorage(PartialStorage[TaskReviewBenchmarkDocument]):
    def __init__(self, tenant: TenantTuple, collection: AsyncCollection):
        super().__init__(tenant=tenant, collection=collection, document_type=TaskReviewBenchmarkDocument)

    async def get_review_benchmark(self, task_id: str, task_schema_id: int):
        document = await self._find_one(
            {"task_id": task_id, "task_schema_id": task_schema_id},
            hint=_BY_TASK_SCHEMA_UNIQUE,
        )
        return document.to_domain()

    async def update_review_aggregates(
        self,
        task_id: str,
        task_schema_id: int,
        iteration: int,
        positive_review_count: int,
        positive_user_review_count: int,
        negative_review_count: int,
        negative_user_review_count: int,
        unsure_review_count: int,
        in_progress_review_count: int,
    ):
        await self._update_one(
            {"task_id": task_id, "task_schema_id": task_schema_id, "results": {"$elemMatch": {"iteration": iteration}}},
            {
                "$set": {
                    "results.$.positive_review_count": positive_review_count,
                    "results.$.positive_user_review_count": positive_user_review_count,
                    "results.$.negative_review_count": negative_review_count,
                    "results.$.negative_user_review_count": negative_user_review_count,
                    "results.$.unsure_review_count": unsure_review_count,
                    "results.$.in_progress_review_count": in_progress_review_count,
                },
            },
            hint=_BY_TASK_SCHEMA_UNIQUE,
        )

    async def add_in_progress_run(self, task_id: str, task_schema_id: int, iteration: int, run_id: str):
        await self._update_one(
            {
                "task_id": task_id,
                "task_schema_id": task_schema_id,
                "results": {"$elemMatch": {"iteration": iteration}},
            },
            {"$push": {"results.$.run_in_progress_ids": run_id}},
            hint=_BY_TASK_SCHEMA_UNIQUE,
        )

    def _updates_for_aggregates(self, agg: RunReviewAggregateWithIteration, idx: str, now: datetime):
        yield f"results.{idx}.updated_at", now
        yield f"results.{idx}.total_run_count", agg["total_run_count"]
        yield f"results.{idx}.run_failed_count", agg["failed_run_count"]
        yield f"results.{idx}.run_in_progress_count", agg["in_progress_review_count"]
        yield f"results.{idx}.positive_review_count", agg["positive_review_count"]
        yield f"results.{idx}.positive_user_review_count", agg["positive_user_review_count"]
        yield f"results.{idx}.negative_review_count", agg["negative_review_count"]
        yield f"results.{idx}.negative_user_review_count", agg["negative_user_review_count"]
        yield f"results.{idx}.unsure_review_count", agg["unsure_review_count"]
        yield f"results.{idx}.in_progress_review_count", agg["in_progress_review_count"]
        yield f"results.{idx}.total_run_count", agg["total_run_count"]
        yield f"results.{idx}.run_failed_count", agg["failed_run_count"]
        yield f"results.{idx}.average_cost_usd", agg["average_cost_usd"]
        yield f"results.{idx}.average_duration_seconds", agg["average_duration_seconds"]

    async def complete_run(self, task_id: str, task_schema_id: int, iteration: int, run_id: str):
        await self._update_one(
            {
                "task_id": task_id,
                "task_schema_id": task_schema_id,
                "results": {"$elemMatch": {"iteration": iteration}},
            },
            {"$pull": {"results.$.run_in_progress_ids": run_id}},
            hint=_BY_TASK_SCHEMA_UNIQUE,
            throw_on_not_found=False,
        )

    async def update_benchmark(
        self,
        task_id: str,
        task_schema_id: int,
        aggregates: Iterable[RunReviewAggregateWithIteration],
        now: datetime,
    ):
        sets: dict[str, Any] = {}
        array_filters: list[dict[str, Any]] = []

        for i, agg in enumerate(aggregates):
            # Only updating fields that have not been updated since "now"
            array_filters.append(
                {
                    f"r{i}.iteration": agg["iteration"],
                    "$or": [
                        {f"r{i}.updated_at": {"$exists": False}},
                        {f"r{i}.updated_at": {"$lt": now}},
                    ],
                },
            )

            for k, v in self._updates_for_aggregates(agg, f"$[r{i}]", now):
                # Can't use list comprehension here since we have nested loops
                sets[k] = v  # noqa: PERF403

        await self._update_one(
            {"task_id": task_id, "task_schema_id": task_schema_id},
            {"$set": sets},
            array_filters=array_filters,
            hint=_BY_TASK_SCHEMA_UNIQUE,
        )

    async def mark_as_loading_new_ai_reviewer(
        self,
        task_id: str,
        task_schema_id: int,
        is_loading_new_ai_reviewer: bool,
    ):
        await self._update_one(
            {"task_id": task_id, "task_schema_id": task_schema_id},
            {"$set": {"is_loading_new_ai_reviewer": is_loading_new_ai_reviewer}},
            hint=_BY_TASK_SCHEMA_UNIQUE,
            upsert=True,
        )

    async def add_versions(self, task_id: str, task_schema_id: int, versions: list[tuple[int, TaskGroupProperties]]):
        if len(versions) == 0:
            raise BadRequestError("At least one iteration must be provided")

        if len(versions) == 1:
            iteration, properties = versions[0]
            push = {"iteration": iteration, "properties": dump_model(properties)}
            filter = {"$ne": iteration}
        else:
            push = {"$each": [{"iteration": i, "properties": dump_model(p)} for i, p in versions]}
            filter = {"$nin": [i for i, _ in versions]}

        doc = await self._find_one_and_update(
            {"task_id": task_id, "task_schema_id": task_schema_id, "results.iteration": filter},
            {"$push": {"results": push}},
            hint=_BY_TASK_SCHEMA_UNIQUE,
            return_document=True,
            upsert=True,
        )
        return doc.to_domain()

    async def remove_versions(self, task_id: str, task_schema_id: int, iterations: list[int]):
        if len(iterations) == 0:
            raise BadRequestError("At least one iteration must be provided")

        if len(iterations) == 1:
            iteration = iterations[0]
            filter = iteration
            pull = iteration
        else:
            filter = {"$in": iterations}
            pull = {"$in": iterations}
        doc = await self._find_one_and_update(
            {"task_id": task_id, "task_schema_id": task_schema_id, "results.iteration": filter},
            {"$pull": {"results": {"iteration": pull}}},
            hint=_BY_TASK_SCHEMA_UNIQUE,
            return_document=True,
        )
        return doc.to_domain()

    async def get_benchmark_versions(self, task_id: str, task_schema_id: int) -> set[int]:
        try:
            document = await self._find_one_doc(
                {"task_id": task_id, "task_schema_id": task_schema_id},
                projection={"results.iteration": 1},
            )
        except ObjectNotFoundException:
            return set()

        if "results" not in document:
            return set()
        return {r["iteration"] for r in document["results"]}
