from datetime import datetime, timezone

import pytest
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from core.domain.errors import DuplicateValueError
from core.domain.review_benchmark import ReviewBenchmark
from core.domain.task_group_properties import TaskGroupProperties
from core.storage import ObjectNotFoundException
from core.storage.mongo.models.task_review_benchmarks import TaskReviewBenchmarkDocument
from core.storage.mongo.mongo_storage import MongoStorage
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.reviews_benchmark import MongoReviewsBenchmarkStorage
from core.storage.mongo.utils import dump_model
from core.storage.review_benchmark_storage import RunReviewAggregateWithIteration


@pytest.fixture(scope="function")
def reviews_benchmark_storage(storage: MongoStorage):
    return storage.review_benchmarks


def _review_benchmark_doc(
    task_id: str = "hello",
    task_schema_id: int = 1,
    results: list[TaskReviewBenchmarkDocument.VersionAggregation] | None = None,
):
    return TaskReviewBenchmarkDocument(
        tenant="test_tenant",
        task_id=task_id,
        task_schema_id=task_schema_id,
        is_loading_new_ai_reviewer=False,
        results=results
        or [
            TaskReviewBenchmarkDocument.VersionAggregation(
                iteration=1,
                properties={
                    "model": "gpt-4o-2024-08-06",
                },
            ),
        ],
    )


async def test_review_benchmark_unique_constraint(reviews_benchmark_col: AsyncCollection):
    # Cleanup
    await reviews_benchmark_col.delete_many({})

    doc = _review_benchmark_doc()
    await reviews_benchmark_col.insert_one(dump_model(doc))

    with pytest.raises(DuplicateKeyError):
        await reviews_benchmark_col.insert_one(dump_model(doc))


class TestGetReviewBenchmark:
    async def test_get_review_benchmark(
        self,
        reviews_benchmark_storage: MongoReviewsBenchmarkStorage,
        reviews_benchmark_col: AsyncCollection,
    ):
        doc = _review_benchmark_doc()
        await reviews_benchmark_col.insert_one(dump_model(doc))

        assert await reviews_benchmark_storage.get_review_benchmark("hello", 1)

    async def test_get_review_benchmark_not_found(
        self,
        reviews_benchmark_storage: MongoReviewsBenchmarkStorage,
        reviews_benchmark_col: AsyncCollection,
    ):
        doc = _review_benchmark_doc()
        await reviews_benchmark_col.insert_one(dump_model(doc))

        with pytest.raises(ObjectNotFoundException):
            await reviews_benchmark_storage.get_review_benchmark("hello", 2)


def _domain_version_aggregation(
    iteration: int = 1,
    properties: TaskGroupProperties | None = None,
    model: str = "gpt-4o-2024-08-06",
    positive_review_count: int = 0,
    negative_review_count: int = 0,
    positive_user_review_count: int = 0,
    negative_user_review_count: int = 0,
    unsure_review_count: int = 0,
    in_progress_review_count: int = 0,
    total_run_count: int = 0,
    run_failed_count: int = 0,
    run_in_progress_count: int = 0,
    average_cost_usd: float | None = None,
    average_duration_seconds: float | None = None,
):
    return ReviewBenchmark.VersionAggregation(
        iteration=iteration,
        properties=properties or TaskGroupProperties(model=model),
        positive_review_count=positive_review_count,
        negative_review_count=negative_review_count,
        positive_user_review_count=positive_user_review_count,
        negative_user_review_count=negative_user_review_count,
        unsure_review_count=unsure_review_count,
        in_progress_review_count=in_progress_review_count,
        total_run_count=total_run_count,
        run_failed_count=run_failed_count,
        run_in_progress_count=run_in_progress_count,
        average_cost_usd=average_cost_usd,
        average_duration_seconds=average_duration_seconds,
    )


class TestAddVersionsToReviewBenchmark:
    async def test_add_single_version_upsert(
        self,
        reviews_benchmark_storage: MongoReviewsBenchmarkStorage,
        reviews_benchmark_col: AsyncCollection,
    ):
        found = await reviews_benchmark_storage.add_versions(
            "hello",
            1,
            [(1, TaskGroupProperties(model="gpt-4o-2024-08-06"))],
        )

        assert found == ReviewBenchmark(
            task_id="hello",
            task_schema_id=1,
            is_loading_new_ai_reviewer=False,
            results=[_domain_version_aggregation()],
        )

        assert found == await reviews_benchmark_storage.get_review_benchmark("hello", 1)

    async def test_add_single_to_existing(
        self,
        reviews_benchmark_storage: MongoReviewsBenchmarkStorage,
        reviews_benchmark_col: AsyncCollection,
    ):
        doc = _review_benchmark_doc()
        await reviews_benchmark_col.insert_one(dump_model(doc))

        found = await reviews_benchmark_storage.add_versions("hello", 1, [(2, TaskGroupProperties(model="hello"))])

        assert found == ReviewBenchmark(
            task_id="hello",
            task_schema_id=1,
            is_loading_new_ai_reviewer=False,
            results=[
                _domain_version_aggregation(iteration=1),
                _domain_version_aggregation(iteration=2, model="hello"),
            ],
        )

    async def test_add_single_duplicate_iteration(
        self,
        reviews_benchmark_storage: MongoReviewsBenchmarkStorage,
        reviews_benchmark_col: AsyncCollection,
    ):
        doc = _review_benchmark_doc()
        await reviews_benchmark_col.insert_one(dump_model(doc))

        with pytest.raises(DuplicateValueError):
            await reviews_benchmark_storage.add_versions("hello", 1, [(1, TaskGroupProperties(model="hello"))])

    async def test_add_multiple_to_existing(
        self,
        reviews_benchmark_storage: MongoReviewsBenchmarkStorage,
        reviews_benchmark_col: AsyncCollection,
    ):
        doc = _review_benchmark_doc()
        await reviews_benchmark_col.insert_one(dump_model(doc))

        found = await reviews_benchmark_storage.add_versions(
            "hello",
            1,
            [
                (2, TaskGroupProperties(model="hello")),
                (3, TaskGroupProperties(model="hello2")),
            ],
        )

        assert found == ReviewBenchmark(
            task_id="hello",
            task_schema_id=1,
            is_loading_new_ai_reviewer=False,
            results=[
                _domain_version_aggregation(iteration=1),
                _domain_version_aggregation(iteration=2, model="hello"),
                _domain_version_aggregation(iteration=3, model="hello2"),
            ],
        )

    async def test_add_multiple_duplicate_iteration(
        self,
        reviews_benchmark_storage: MongoReviewsBenchmarkStorage,
        reviews_benchmark_col: AsyncCollection,
    ):
        doc = _review_benchmark_doc()
        await reviews_benchmark_col.insert_one(dump_model(doc))

        with pytest.raises(DuplicateValueError):
            await reviews_benchmark_storage.add_versions(
                "hello",
                1,
                [
                    (1, TaskGroupProperties(model="hello")),
                    (3, TaskGroupProperties(model="hello2")),
                ],
            )

        found = await reviews_benchmark_storage.get_review_benchmark("hello", 1)
        assert len(found.results) == 1


class TestRemoveVersionsFromReviewBenchmark:
    async def test_remove_single_version(
        self,
        reviews_benchmark_storage: MongoReviewsBenchmarkStorage,
        reviews_benchmark_col: AsyncCollection,
    ):
        doc = _review_benchmark_doc()
        await reviews_benchmark_col.insert_one(dump_model(doc))

        found = await reviews_benchmark_storage.remove_versions("hello", 1, [1])

        assert found == ReviewBenchmark(
            task_id="hello",
            task_schema_id=1,
            is_loading_new_ai_reviewer=False,
            results=[],
        )

    async def test_remove_multiple_versions(
        self,
        reviews_benchmark_storage: MongoReviewsBenchmarkStorage,
        reviews_benchmark_col: AsyncCollection,
    ):
        doc = _review_benchmark_doc(
            results=[
                TaskReviewBenchmarkDocument.VersionAggregation(
                    iteration=1,
                    properties={
                        "model": "gpt-4o-2024-08-06",
                    },
                ),
                TaskReviewBenchmarkDocument.VersionAggregation(
                    iteration=2,
                    properties={
                        "model": "gpt-4o-2024-08-06",
                    },
                ),
                TaskReviewBenchmarkDocument.VersionAggregation(
                    iteration=3,
                    properties={
                        "model": "gpt-4o-2024-08-06",
                    },
                ),
            ],
        )
        await reviews_benchmark_col.insert_one(dump_model(doc))

        found = await reviews_benchmark_storage.remove_versions("hello", 1, [1, 2])

        assert found == ReviewBenchmark(
            task_id="hello",
            task_schema_id=1,
            is_loading_new_ai_reviewer=False,
            results=[_domain_version_aggregation(iteration=3)],
        )


class TestUpdateBenchmark:
    @pytest.fixture
    async def inserted_benchmark(self, reviews_benchmark_col: AsyncCollection):
        doc = _review_benchmark_doc(
            results=[
                TaskReviewBenchmarkDocument.VersionAggregation(
                    iteration=1,
                    properties={
                        "model": "gpt-4o-2024-08-06",
                    },
                    positive_review_count=1,
                    negative_review_count=1,
                    positive_user_review_count=1,
                    negative_user_review_count=1,
                    run_in_progress_ids=["1"],
                ),
                TaskReviewBenchmarkDocument.VersionAggregation(
                    iteration=2,
                    properties={
                        "model": "gpt-4o-2024-08-06",
                    },
                    total_run_count=1,
                    run_failed_count=1,
                    updated_at=datetime(2022, 1, 1, tzinfo=timezone.utc),
                ),
            ],
        )
        res = await reviews_benchmark_col.insert_one(dump_model(doc))
        doc.id = res.inserted_id
        return doc

    def _review_agg(self, iteration: int = 1, positive_review_count: int = 2):
        return RunReviewAggregateWithIteration(
            iteration=iteration,
            positive_review_count=positive_review_count,
            negative_review_count=3,
            positive_user_review_count=4,
            negative_user_review_count=5,
            unsure_review_count=6,
            in_progress_review_count=7,
            total_run_count=8,
            failed_run_count=9,
            average_cost_usd=10,
            average_duration_seconds=11,
        )

    async def test_update_single(
        self,
        reviews_benchmark_storage: MongoReviewsBenchmarkStorage,
        inserted_benchmark: TaskReviewBenchmarkDocument,
        reviews_benchmark_col: AsyncCollection,
    ):
        await reviews_benchmark_storage.update_benchmark(
            inserted_benchmark.task_id,
            inserted_benchmark.task_schema_id,
            aggregates=[self._review_agg()],
            now=datetime(2022, 1, 2, tzinfo=timezone.utc),
        )

        found = await reviews_benchmark_storage.get_review_benchmark(
            inserted_benchmark.task_id,
            inserted_benchmark.task_schema_id,
        )
        iteration_1 = next(a for a in found.results if a.iteration == 1)
        assert iteration_1.positive_review_count == 2
        assert iteration_1.negative_review_count == 3
        assert iteration_1.positive_user_review_count == 4
        assert iteration_1.negative_user_review_count == 5
        assert iteration_1.unsure_review_count == 6
        assert iteration_1.in_progress_review_count == 7
        assert iteration_1.total_run_count == 8
        assert iteration_1.run_failed_count == 9
        assert iteration_1.average_cost_usd == 10
        assert iteration_1.average_duration_seconds == 11
        assert iteration_1.run_in_progress_count == 1

        # Check that the second iteration was not updated
        iteration_2 = next(a for a in found.results if a.iteration == 2)
        assert iteration_2 == inserted_benchmark.results[1].to_domain()

        doc = await reviews_benchmark_col.find_one({"_id": ObjectId(inserted_benchmark.id)})
        assert doc
        # Should be unchanged
        assert doc["results"][1]["updated_at"] == datetime(2022, 1, 1, tzinfo=timezone.utc)
        # Should be updated
        assert doc["results"][0]["updated_at"] == datetime(2022, 1, 2, tzinfo=timezone.utc)

        # Now update with a previous date
        await reviews_benchmark_storage.update_benchmark(
            inserted_benchmark.task_id,
            inserted_benchmark.task_schema_id,
            # Changing the positive review count
            aggregates=[self._review_agg(positive_review_count=1000)],
            # But having a date in the past
            now=datetime(2022, 1, 1, tzinfo=timezone.utc),
        )
        found = await reviews_benchmark_storage.get_review_benchmark(
            inserted_benchmark.task_id,
            inserted_benchmark.task_schema_id,
        )
        assert found.results[0].positive_review_count == 2
        assert found.results[1].positive_review_count == 0


class TestGetBenchmarkVersions:
    async def test_get_benchmark_versions(
        self,
        reviews_benchmark_storage: MongoReviewsBenchmarkStorage,
        reviews_benchmark_col: AsyncCollection,
    ):
        await reviews_benchmark_col.insert_one(
            dump_model(
                _review_benchmark_doc(
                    results=[
                        TaskReviewBenchmarkDocument.VersionAggregation(iteration=1, properties={}),
                        TaskReviewBenchmarkDocument.VersionAggregation(iteration=2, properties={}),
                    ],
                ),
            ),
        )

        assert await reviews_benchmark_storage.get_benchmark_versions("hello", 1) == {1, 2}

    # Check that when the benchmark is not found, an empty set is returned
    async def test_get_benchmark_versions_not_found(
        self,
        reviews_benchmark_storage: MongoReviewsBenchmarkStorage,
    ):
        assert await reviews_benchmark_storage.get_benchmark_versions("hello", 1) == set()


class TestCompleteRun:
    async def test_complete_run(
        self,
        reviews_benchmark_storage: MongoReviewsBenchmarkStorage,
        reviews_benchmark_col: AsyncCollection,
    ):
        res = await reviews_benchmark_col.insert_one(
            dump_model(
                _review_benchmark_doc(
                    results=[
                        TaskReviewBenchmarkDocument.VersionAggregation(
                            iteration=1,
                            properties={},
                            run_in_progress_ids=["a"],
                        ),
                        TaskReviewBenchmarkDocument.VersionAggregation(iteration=2, properties={}),
                    ],
                ),
            ),
        )

        await reviews_benchmark_storage.complete_run("hello", 1, 1, "a")

        doc = await reviews_benchmark_col.find_one({"_id": res.inserted_id})
        assert doc and doc["results"][0]["run_in_progress_ids"] == []

        # Check that we don't throw on not found
        await reviews_benchmark_storage.complete_run("hello", 1, 1, "a")
