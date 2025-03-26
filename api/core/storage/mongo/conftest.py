import os
from asyncio import gather

import pytest

from core.storage.mongo.migrations.migrate import migrate
from core.storage.mongo.mongo_storage import MongoStorage
from core.storage.mongo.mongo_types import AsyncCollection
from core.utils import no_op
from core.utils.encryption import Encryption

TENANT = "test_tenant"


@pytest.fixture(scope="session")
def mongo_test_uri() -> str:
    uri = os.environ["WORKFLOWAI_TEST_MONGO_CONNECTION_STRING"]
    if "localhost" not in uri:
        raise ValueError("This test is only for localhost databases")
    return uri


@pytest.fixture(scope="function")
def base_storage(
    mock_encryption: Encryption,
    mongo_test_uri: str,
) -> MongoStorage:
    return MongoStorage(
        tenant=TENANT,
        tenant_uid=1,
        connection_string=mongo_test_uri,
        encryption=mock_encryption,
        event_router=no_op.event_router,
    )


@pytest.fixture(scope="function")
def tasks_col(base_storage: MongoStorage) -> AsyncCollection:
    return base_storage._tasks_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def task_variants_col(base_storage: MongoStorage) -> AsyncCollection:
    return base_storage._task_variants_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def task_run_col(base_storage: MongoStorage) -> AsyncCollection:
    return base_storage._task_runs_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def task_example_col(base_storage: MongoStorage) -> AsyncCollection:
    return base_storage._task_examples_collections  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def task_schema_id_col(base_storage: MongoStorage) -> AsyncCollection:
    return base_storage._task_schema_id_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def task_run_group_col(base_storage: MongoStorage) -> AsyncCollection:
    return base_storage._task_run_group_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def task_run_group_idx_col(base_storage: MongoStorage) -> AsyncCollection:
    return base_storage._task_run_group_idx_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def org_col(base_storage: MongoStorage) -> AsyncCollection:
    return base_storage._organization_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def task_schemas_col(base_storage: MongoStorage) -> AsyncCollection:
    return base_storage._task_schemas_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def tasks_benchmarks_col(base_storage: MongoStorage) -> AsyncCollection:
    return base_storage._task_benchmarks_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def changelogs_col(base_storage: MongoStorage) -> AsyncCollection:
    return base_storage._changelogs_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def collection(base_storage: MongoStorage) -> AsyncCollection:
    return base_storage._get_collection(  # type:ignore
        os.environ.get("WORKFLOWAI_TEST_MONGO_COLLECTION", "test"),
    )


@pytest.fixture(scope="function")
def task_evaluators_col(base_storage: MongoStorage) -> AsyncCollection:
    return base_storage._task_evaluators_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def task_inputs_col(base_storage: MongoStorage) -> AsyncCollection:
    return base_storage._task_inputs_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def migrations_col(base_storage: MongoStorage) -> AsyncCollection:
    return base_storage._migrations_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def dataset_benchmarks_col(base_storage: MongoStorage):
    return base_storage._dataset_benchmarks_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def reviews_col(base_storage: MongoStorage):
    return base_storage._reviews_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def task_group_semvers_col(base_storage: MongoStorage):
    return base_storage._task_group_semvers_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
async def system_profile_col(base_storage: MongoStorage):
    db = base_storage._db  # pyright: ignore [reportPrivateUsage]
    await db.command({"profile": 2})
    yield db["system.profile"]
    # Reset profiling
    await db.command({"profile": 0})


@pytest.fixture(scope="function")
def input_evaluations_col(base_storage: MongoStorage):
    return base_storage._input_evaluations_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def reviews_benchmark_col(base_storage: MongoStorage):
    return base_storage._review_benchmarks_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def task_deployments_col(base_storage: MongoStorage):
    return base_storage._task_deployments_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def feedback_col(base_storage: MongoStorage):
    return base_storage._feedback_collection  # pyright: ignore [reportPrivateUsage]


@pytest.fixture(scope="function")
def all_collections(
    task_example_col: AsyncCollection,
    task_run_col: AsyncCollection,
    task_run_group_col: AsyncCollection,
    task_run_group_idx_col: AsyncCollection,
    task_variants_col: AsyncCollection,
    task_schema_id_col: AsyncCollection,
    org_col: AsyncCollection,
    task_schemas_col: AsyncCollection,
    tasks_benchmarks_col: AsyncCollection,
    task_evaluators_col: AsyncCollection,
    tasks_col: AsyncCollection,
    task_inputs_col: AsyncCollection,
    migrations_col: AsyncCollection,
    dataset_benchmarks_col: AsyncCollection,
    input_evaluations_col: AsyncCollection,
    reviews_col: AsyncCollection,
    reviews_benchmark_col: AsyncCollection,
    task_deployments_col: AsyncCollection,
    task_group_semvers_col: AsyncCollection,
    changelogs_col: AsyncCollection,
    feedback_col: AsyncCollection,
) -> list[AsyncCollection]:
    return [
        task_example_col,
        task_run_col,
        task_run_group_col,
        task_run_group_idx_col,
        task_variants_col,
        task_schema_id_col,
        org_col,
        task_schemas_col,
        tasks_benchmarks_col,
        task_evaluators_col,
        tasks_col,
        task_inputs_col,
        migrations_col,
        dataset_benchmarks_col,
        input_evaluations_col,
        reviews_col,
        reviews_benchmark_col,
        task_deployments_col,
        task_group_semvers_col,
        changelogs_col,
        feedback_col,
    ]


@pytest.fixture(scope="function")
async def empty_storage(
    base_storage: MongoStorage,
    all_collections: list[AsyncCollection],
    collection: AsyncCollection,
) -> MongoStorage:
    await gather(*[col.delete_many({}) for col in all_collections], collection.delete_many({}))

    return base_storage


@pytest.fixture(scope="function")
async def storage(empty_storage: MongoStorage) -> MongoStorage:
    await migrate(empty_storage)
    return empty_storage
