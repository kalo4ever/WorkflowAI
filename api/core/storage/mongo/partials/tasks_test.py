from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
from pymongo.errors import DuplicateKeyError

from core.domain.ban import Ban
from core.domain.task_info import TaskInfo
from core.storage.models import TaskUpdate
from core.storage.mongo.models.task import TaskDocument
from core.storage.mongo.mongo_storage import MongoStorage
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.task_variants import MongoTaskVariantsStorage
from core.storage.mongo.partials.tasks import MongoTaskStorage
from core.storage.mongo.utils import dump_model


@pytest.fixture(scope="function")
def mock_task_variants_storage():
    return Mock(spec=MongoTaskVariantsStorage)


@pytest.fixture(scope="function")
def task_storage(storage: MongoStorage, mock_task_variants_storage: Mock):
    tasks = storage.tasks
    tasks._task_variants = mock_task_variants_storage  # pyright: ignore [reportPrivateUsage]
    return tasks


class TestUnique:
    async def test_uid_unique(self, task_storage: MongoTaskStorage, tasks_col: AsyncCollection):
        await tasks_col.insert_one({"task_id": "bla", "tenant": "test_tenant", "uid": 1})

        with pytest.raises(DuplicateKeyError):
            await tasks_col.insert_one({"task_id": "bla1", "tenant": "tenant1", "uid": 1})

    async def test_uid_upsert(self, task_storage: MongoTaskStorage, tasks_col: AsyncCollection):
        inserted = await tasks_col.insert_one({"task_id": "bla", "tenant": "test_tenant", "uid": 1})

        # Updating existing task should not change the uid
        await task_storage.update_task("bla", TaskUpdate(is_public=True))

        updated = await tasks_col.find_one({"uid": 1})
        assert updated and updated["_id"] == inserted.inserted_id

        await task_storage.update_task("blabli", TaskUpdate(is_public=False))
        upserted = await tasks_col.find_one({"task_id": "blabli"})
        assert upserted and upserted["uid"]


class TestSetTaskPublic:
    async def test_not_exist(
        self,
        task_storage: MongoTaskStorage,
        tasks_col: AsyncCollection,
        mock_task_variants_storage: Mock,
    ):
        assert await tasks_col.find_one({"task_id": "bla"}) is None

        await task_storage.update_task("bla", TaskUpdate(is_public=True))

        doc = await tasks_col.find_one({"task_id": "bla"})
        assert doc
        assert doc["tenant"] == "test_tenant"
        assert doc["is_public"] is True

        mock_task_variants_storage.update_task.assert_called_once_with("bla", True, None)

    async def test_exist(
        self,
        task_storage: MongoTaskStorage,
        tasks_col: AsyncCollection,
        mock_task_variants_storage: Mock,
    ):
        await tasks_col.insert_one({"task_id": "bla", "tenant": "test_tenant", "is_public": False})

        await task_storage.update_task("bla", TaskUpdate(is_public=True))

        doc = await tasks_col.find_one({"task_id": "bla"})
        assert doc
        assert doc["tenant"] == "test_tenant"
        assert doc["is_public"] is True

        mock_task_variants_storage.update_task.assert_called_once_with("bla", True, None)


class TestIsTaskPublic:
    async def test_not_exist(self, task_storage: MongoTaskStorage):
        assert await task_storage.is_task_public("bla") is False

    async def test_exist(self, task_storage: MongoTaskStorage, tasks_col: AsyncCollection):
        await tasks_col.insert_one({"task_id": "bla", "tenant": "test_tenant", "is_public": True})

        assert await task_storage.is_task_public("bla") is True

    async def test_flow(self, task_storage: MongoTaskStorage):
        assert await task_storage.is_task_public("bla") is False

        await task_storage.update_task("bla", TaskUpdate(is_public=True))

        assert await task_storage.is_task_public("bla") is True

        await task_storage.update_task("bla", TaskUpdate(is_public=False))

        assert await task_storage.is_task_public("bla") is False


class TestIsTaskBanned:
    async def test_is_task_banned(self, task_storage: MongoTaskStorage, tasks_col: AsyncCollection):
        banned_at = datetime(2024, 1, 1, 0, 0, 0, 0, timezone.utc)

        await task_storage.update_task(
            "task_id",
            TaskUpdate(
                ban=Ban(
                    reason="task_run_non_compliant",
                    related_ids=["run1"],
                    banned_at=banned_at,
                ),
            ),
        )

        doc = await tasks_col.find_one({"task_id": "task_id"})
        assert doc
        assert doc["ban"] == {
            "reason": "task_run_non_compliant",
            "related_ids": ["run1"],
            "banned_at": banned_at,
        }


class TestTaskHide:
    async def test_hide(self, task_storage: MongoTaskStorage):
        await task_storage.update_task("bla", TaskUpdate(hide_schema=1))

        info = await task_storage.get_task_info("bla")
        assert info.uid
        info = TaskInfo(
            uid=info.uid,
            task_id="bla",
            name="",
            is_public=False,
            hidden_schema_ids=[1],
        )

        await task_storage.update_task("bla", TaskUpdate(unhide_schema=1))

        assert await task_storage.get_task_info("bla") == TaskInfo(
            uid=info.uid,
            task_id="bla",
            name="",
            is_public=False,
            hidden_schema_ids=[],
        )


class TestSchemaLastActiveAt:
    # task_storage is added first to make sure the collection is cleaned up
    @pytest.fixture(autouse=True)
    async def inserted_task_doc(self, task_storage: MongoTaskStorage, tasks_col: AsyncCollection):
        doc = TaskDocument(task_id="bla", tenant="test_tenant")
        await tasks_col.insert_one(dump_model(doc))
        return doc

    async def test_update_last_active_at(self, task_storage: MongoTaskStorage):
        now = datetime.now(timezone.utc)
        await task_storage.update_task("bla", TaskUpdate(schema_last_active_at=(1, now)))

        actual = await task_storage.get_task_info("bla")
        assert actual.schema_details is not None
        assert len(actual.schema_details) == 1
        assert actual.schema_details[0]["schema_id"] == 1
        assert abs(actual.schema_details[0]["last_active_at"] - now) < timedelta(seconds=1)

    async def test_update_last_active_at_twice(self, task_storage: MongoTaskStorage):
        now = datetime.now(timezone.utc)
        await task_storage.update_task_schema_details("bla", 1, now - timedelta(minutes=20))
        await task_storage.update_task_schema_details("bla", 1, now)
        await task_storage.update_task_schema_details("bla", 1, now)

        actual = await task_storage.get_task_info("bla")
        assert actual.schema_details is not None
        assert len(actual.schema_details) == 1
        assert actual.schema_details[0]["schema_id"] == 1
        assert abs(actual.schema_details[0]["last_active_at"] - now) < timedelta(seconds=1)

    async def test_update_last_active_at_with_different_schema_id(self, task_storage: MongoTaskStorage):
        now = datetime.now(timezone.utc)
        await task_storage.update_task("bla", TaskUpdate(schema_last_active_at=(1, now - timedelta(minutes=20))))
        await task_storage.update_task("bla", TaskUpdate(schema_last_active_at=(2, now)))

        actual = await task_storage.get_task_info("bla")
        assert actual.schema_details is not None
        assert len(actual.schema_details) == 2
        assert actual.schema_details[0]["schema_id"] == 1
        assert actual.schema_details[1]["schema_id"] == 2
        assert abs(actual.schema_details[0]["last_active_at"] - (now - timedelta(minutes=20))) < timedelta(seconds=1)
        assert abs(actual.schema_details[1]["last_active_at"] - now) < timedelta(seconds=1)

        await task_storage.update_task("bla", TaskUpdate(schema_last_active_at=(1, now)))

        actual = await task_storage.get_task_info("bla")
        assert actual.schema_details is not None
        assert len(actual.schema_details) == 2
        assert actual.schema_details[0]["schema_id"] == 1
        assert actual.schema_details[1]["schema_id"] == 2
        assert abs(actual.schema_details[0]["last_active_at"] - now) < timedelta(seconds=1)
        assert abs(actual.schema_details[1]["last_active_at"] - now) < timedelta(seconds=1)
