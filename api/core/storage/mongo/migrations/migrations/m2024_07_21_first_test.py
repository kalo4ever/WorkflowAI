import pytest

from core.storage.mongo.migrations.migrations.m2024_07_21_first import FirstMigration
from core.storage.mongo.mongo_storage import MongoStorage
from core.storage.mongo.mongo_types import AsyncCollection
from tests.utils import fixtures_json


@pytest.fixture(scope="function")
async def first_migration(empty_storage: MongoStorage):
    return FirstMigration(empty_storage)


async def test_migrate_runs(task_run_col: AsyncCollection, first_migration: FirstMigration) -> None:
    # Clean up all indices
    await task_run_col.drop_indexes()

    await task_run_col.insert_many(fixtures_json("db", "task_runs.json", bson=True))

    await first_migration.create_task_run_indices()


async def test_migrate_benchmarks(tasks_benchmarks_col: AsyncCollection, first_migration: FirstMigration) -> None:
    # Clean up all indices
    await tasks_benchmarks_col.drop_indexes()

    await tasks_benchmarks_col.insert_many(fixtures_json("db", "benchmarks.json", bson=True))

    await first_migration.create_task_benchmarks_indices()
