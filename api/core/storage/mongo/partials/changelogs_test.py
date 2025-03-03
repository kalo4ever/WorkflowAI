import pytest

from core.domain.changelogs import VersionChangelog
from core.domain.errors import DuplicateValueError
from core.storage.mongo.conftest import TENANT
from core.storage.mongo.models.changelog import ChangeLogDocument
from core.storage.mongo.mongo_storage import MongoStorage
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.changelogs import MongoChangeLogStorage
from core.storage.mongo.utils import dump_model


@pytest.fixture(scope="function")
def changelog_storage(storage: MongoStorage):
    return storage.changelogs


class TestInsertChangelog:
    async def test_insert_changelog(
        self,
        changelog_storage: MongoChangeLogStorage,
        changelogs_col: AsyncCollection,
    ):
        # Create a changelog domain object
        changelog = VersionChangelog(
            task_id="task_id",
            task_schema_id=1,
            major_from=1,
            major_to=2,
            similarity_hash_from="hash1",
            similarity_hash_to="hash2",
            changelog=["change 1", "change 2"],
        )

        # Insert the changelog
        result = await changelog_storage.insert_changelog(changelog)

        # Verify the returned domain object
        assert result.task_id == "task_id"
        assert result.task_schema_id == 1
        assert result.major_from == 1
        assert result.major_to == 2
        assert result.similarity_hash_from == "hash1"
        assert result.similarity_hash_to == "hash2"
        assert result.changelog == ["change 1", "change 2"]

        # Verify the document in the database
        doc = await changelogs_col.find_one({"task_id": "task_id", "task_schema_id": 1})
        assert doc is not None
        assert doc["task_id"] == "task_id"
        assert doc["task_schema_id"] == 1
        assert doc["major_from"] == 1
        assert doc["major_to"] == 2
        assert doc["similarity_hash_from"] == "hash1"
        assert doc["similarity_hash_to"] == "hash2"
        assert doc["changelog"] == ["change 1", "change 2"]

    async def test_insert_changelog_duplicate(self, changelog_storage: MongoChangeLogStorage):
        changelog = VersionChangelog(
            task_id="task_id",
            task_schema_id=1,
            major_from=1,
            major_to=2,
            similarity_hash_from="hash1",
            similarity_hash_to="hash2",
            changelog=["change 1", "change 2"],
        )
        await changelog_storage.insert_changelog(changelog)

        # try inserting a changelog with the same similarity_hash_to
        changelog2 = changelog.model_copy(update={"similarity_hash_from": "hash2"})
        with pytest.raises(DuplicateValueError):
            await changelog_storage.insert_changelog(changelog2)

        # confirming that changing the similarity_hash_to does not raise the error
        changelog3 = changelog2.model_copy(update={"similarity_hash_to": "hash3"})
        await changelog_storage.insert_changelog(changelog3)


class TestListChangelogs:
    async def test_list_changelogs_with_schema_id(
        self,
        changelog_storage: MongoChangeLogStorage,
        changelogs_col: AsyncCollection,
    ):
        # Insert test documents
        docs = [
            ChangeLogDocument(
                tenant=TENANT,
                task_id="task_id",
                task_schema_id=1,
                major_from=1,
                major_to=2,
                similarity_hash_from="hash1",
                similarity_hash_to="hash2",
                changelog=["change 1"],
            ),
            ChangeLogDocument(
                tenant=TENANT,
                task_id="task_id",
                task_schema_id=1,
                major_from=2,
                major_to=3,
                similarity_hash_from="hash2",
                similarity_hash_to="hash3",
                changelog=["change 2"],
            ),
        ]
        await changelogs_col.insert_many([dump_model(doc) for doc in docs])

        # List changelogs with schema_id filter
        changelogs = [c async for c in changelog_storage.list_changelogs("task_id", 1)]

        assert len(changelogs) == 2
        assert all(isinstance(cl, VersionChangelog) for cl in changelogs)
        assert changelogs[0].major_from == 1
        assert changelogs[1].major_to == 3

    async def test_list_changelogs_without_schema_id(
        self,
        changelog_storage: MongoChangeLogStorage,
        changelogs_col: AsyncCollection,
    ):
        # Insert test documents with different schema_ids
        docs = [
            ChangeLogDocument(
                tenant=TENANT,
                task_id="task_id",
                task_schema_id=1,
                major_from=1,
                major_to=2,
                similarity_hash_from="hash1",
                similarity_hash_to="hash2",
                changelog=["change 1"],
            ),
            ChangeLogDocument(
                tenant=TENANT,
                task_id="task_id",
                task_schema_id=2,
                major_from=1,
                major_to=2,
                similarity_hash_from="hash3",
                similarity_hash_to="hash4",
                changelog=["change 2"],
            ),
        ]
        await changelogs_col.insert_many([dump_model(doc) for doc in docs])

        # List changelogs without schema_id filter
        changelogs = [c async for c in changelog_storage.list_changelogs("task_id", None)]

        assert len(changelogs) == 2
        assert all(isinstance(cl, VersionChangelog) for cl in changelogs)
        schema_ids = {cl.task_schema_id for cl in changelogs}
        assert schema_ids == {1, 2}

    async def test_list_changelogs_empty_result(
        self,
        changelog_storage: MongoChangeLogStorage,
    ):
        changelogs = [c async for c in changelog_storage.list_changelogs("non_existent_task", None)]
        assert len(changelogs) == 0
