import asyncio

import pytest

from core.domain.errors import DuplicateValueError
from core.domain.major_minor import MajorMinor
from core.storage.mongo.conftest import TENANT
from core.storage.mongo.models.task_group_semver import TaskGroupSemverDocument
from core.storage.mongo.mongo_storage import MongoStorage
from core.storage.mongo.mongo_storage_test import TASK_ID
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.task_group_semvers import TaskGroupSemverStorage
from core.storage.mongo.utils import dump_model


@pytest.fixture(scope="function")
def task_group_semvers_storage(storage: MongoStorage) -> TaskGroupSemverStorage:
    return storage.task_group_semvers


class TestInsertNewSemverDoc:
    async def test_first_major_version(
        self,
        task_group_semvers_storage: TaskGroupSemverStorage,
        task_group_semvers_col: AsyncCollection,
    ):
        """Test inserting the first major version when no previous versions exist."""

        # Insert the first version
        result = await task_group_semvers_storage._insert_new_semver_doc(  # pyright: ignore[reportPrivateUsage]
            task_id=TASK_ID,
            similarity_hash="test_hash",
            properties_hash="prop_hash",
        )

        # Check the returned MajorMinor
        assert result == MajorMinor(major=1, minor=1)

        # Verify the document in the database
        doc = await task_group_semvers_col.find_one({"task_id": TASK_ID})
        assert doc is not None
        assert doc["major"] == 1
        assert doc["max_minor"] == 1
        assert doc["similarity_hash"] == "test_hash"
        assert len(doc["minors"]) == 1
        assert doc["minors"][0]["minor"] == 1
        assert doc["minors"][0]["properties_hash"] == "prop_hash"

    async def test_subsequent_major_version(
        self,
        task_group_semvers_storage: TaskGroupSemverStorage,
        task_group_semvers_col: AsyncCollection,
    ):
        """Test inserting a new major version when previous versions exist."""

        # Insert an existing document with major version 2
        existing_doc = TaskGroupSemverDocument(
            tenant=TENANT,
            task_id=TASK_ID,
            similarity_hash="existing_hash",
            major=2,
            max_minor=1,
            minors=[TaskGroupSemverDocument.Minor(minor=1, properties_hash="existing_prop_hash")],
        )
        await task_group_semvers_col.insert_one(dump_model(existing_doc))

        # Insert a new version
        result = await task_group_semvers_storage._insert_new_semver_doc(  # pyright: ignore[reportPrivateUsage]
            task_id=TASK_ID,
            similarity_hash="new_hash",
            properties_hash="new_prop_hash",
        )

        # Check the returned MajorMinor
        assert result == MajorMinor(major=3, minor=1)

        # Verify both documents exist in the database
        docs = [d async for d in task_group_semvers_col.find({"task_id": TASK_ID})]
        assert len(docs) == 2

        # Find the new document
        new_doc = next(d for d in docs if d["major"] == 3)
        assert new_doc["similarity_hash"] == "new_hash"
        assert new_doc["max_minor"] == 1
        assert len(new_doc["minors"]) == 1
        assert new_doc["minors"][0]["minor"] == 1
        assert new_doc["minors"][0]["properties_hash"] == "new_prop_hash"

    async def test_duplicate_similarity_hash(
        self,
        task_group_semvers_storage: TaskGroupSemverStorage,
        task_group_semvers_col: AsyncCollection,
    ):
        """Test that inserting a document with a duplicate similarity hash raises an error."""
        task_id = "test_task"
        similarity_hash = "test_hash"

        # Insert first document
        existing_doc = TaskGroupSemverDocument(
            tenant=TENANT,
            task_id=task_id,
            similarity_hash=similarity_hash,
            major=1,
            max_minor=1,
            minors=[TaskGroupSemverDocument.Minor(minor=1, properties_hash="existing_prop_hash")],
        )
        await task_group_semvers_col.insert_one(dump_model(existing_doc))

        # Attempt to insert another document with the same similarity hash
        with pytest.raises(DuplicateValueError):
            await task_group_semvers_storage._insert_new_semver_doc(  # pyright: ignore[reportPrivateUsage]
                task_id=task_id,
                similarity_hash=similarity_hash,
                properties_hash="new_prop_hash",
            )

    async def test_race_condition(
        self,
        task_group_semvers_storage: TaskGroupSemverStorage,
        task_group_semvers_col: AsyncCollection,
    ):
        """Test that concurrent calls to _insert_new_semver_doc with the same parameters fail gracefully."""
        task_id = "test_task"
        similarity_hash = "test_hash"
        properties_hash = "prop_hash"

        # Create two concurrent calls with the same parameters
        async def insert_doc():
            return await task_group_semvers_storage._insert_new_semver_doc(  # pyright: ignore[reportPrivateUsage]
                task_id=task_id,
                similarity_hash=similarity_hash,
                properties_hash=properties_hash,
            )

        # Run both calls concurrently
        results = await asyncio.gather(insert_doc(), insert_doc(), return_exceptions=True)

        # One call should succeed and one should fail
        success_count = sum(1 for r in results if isinstance(r, MajorMinor))
        error_count = sum(1 for r in results if isinstance(r, DuplicateValueError))
        assert success_count == 1, "Expected exactly one successful call"
        assert error_count == 1, "Expected exactly one failed call"

        # Verify only one document was created
        docs = [d async for d in task_group_semvers_col.find({"task_id": task_id})]
        assert len(docs) == 1, "Expected exactly one document to be created"

        # Verify the document has the correct values
        doc = docs[0]
        assert doc["major"] == 1
        assert doc["max_minor"] == 1
        assert doc["similarity_hash"] == similarity_hash
        assert len(doc["minors"]) == 1
        assert doc["minors"][0]["minor"] == 1
        assert doc["minors"][0]["properties_hash"] == properties_hash

    async def test_different_task_id(
        self,
        task_group_semvers_storage: TaskGroupSemverStorage,
        task_group_semvers_col: AsyncCollection,
    ):
        """Test that major versions are independent for different task IDs."""
        similarity_hash = "test_hash"
        properties_hash = "prop_hash"

        # Insert for first task
        result1 = await task_group_semvers_storage._insert_new_semver_doc(  # pyright: ignore[reportPrivateUsage]
            task_id="task1",
            similarity_hash=similarity_hash + "1",
            properties_hash=properties_hash,
        )

        # Insert for second task
        result2 = await task_group_semvers_storage._insert_new_semver_doc(  # pyright: ignore[reportPrivateUsage]
            task_id="task2",
            similarity_hash=similarity_hash + "2",
            properties_hash=properties_hash,
        )

        # Both should start at major version 1
        assert result1 == MajorMinor(major=1, minor=1)
        assert result2 == MajorMinor(major=1, minor=1)

    async def test_different_tenant(
        self,
        task_group_semvers_col: AsyncCollection,
    ):
        """Test that major versions are independent for different tenants."""
        task_id = "test_task"

        similarity_hash = "test_hash"
        properties_hash = "prop_hash"

        # Create storages for different tenants
        storage1 = TaskGroupSemverStorage(("tenant1", 1), task_group_semvers_col)
        storage2 = TaskGroupSemverStorage(("tenant2", 2), task_group_semvers_col)

        # Insert for first tenant
        result1 = await storage1._insert_new_semver_doc(  # pyright: ignore[reportPrivateUsage]
            task_id=task_id,
            similarity_hash=similarity_hash,
            properties_hash=properties_hash,
        )

        # Insert for second tenant
        result2 = await storage2._insert_new_semver_doc(  # pyright: ignore[reportPrivateUsage]
            task_id=task_id,
            similarity_hash=similarity_hash,
            properties_hash=properties_hash,
        )

        # Both should start at major version 1
        assert result1 == MajorMinor(major=1, minor=1)
        assert result2 == MajorMinor(major=1, minor=1)


class TestAttemptAssignSemver:
    async def test_new_major_version(
        self,
        task_group_semvers_storage: TaskGroupSemverStorage,
        task_group_semvers_col: AsyncCollection,
    ):
        """Test when no document exists with the similarity hash."""
        task_id = "test_task"
        similarity_hash = "test_hash"
        properties_hash = "prop_hash"

        # Attempt to assign semver
        result, is_new = await task_group_semvers_storage._attempt_assign_semver(  # pyright: ignore[reportPrivateUsage]
            task_id=task_id,
            similarity_hash=similarity_hash,
            properties_hash=properties_hash,
        )

        # Check the result
        assert result == MajorMinor(major=1, minor=1)
        assert is_new is True

        # Verify the document in the database
        doc = await task_group_semvers_col.find_one({"task_id": task_id})
        assert doc is not None
        assert doc["major"] == 1
        assert doc["max_minor"] == 1
        assert doc["similarity_hash"] == similarity_hash
        assert len(doc["minors"]) == 1
        assert doc["minors"][0]["minor"] == 1
        assert doc["minors"][0]["properties_hash"] == properties_hash

    async def test_existing_version(
        self,
        task_group_semvers_storage: TaskGroupSemverStorage,
        task_group_semvers_col: AsyncCollection,
    ):
        """Test when a document exists with both the similarity hash and properties hash."""
        task_id = "test_task"
        similarity_hash = "test_hash"
        properties_hash = "prop_hash"

        # Insert an existing document
        existing_doc = TaskGroupSemverDocument(
            tenant=TENANT,
            task_id=task_id,
            similarity_hash=similarity_hash,
            major=2,
            max_minor=1,
            minors=[TaskGroupSemverDocument.Minor(minor=1, properties_hash=properties_hash)],
        )
        await task_group_semvers_col.insert_one(dump_model(existing_doc))

        # Attempt to assign semver
        result, is_new = await task_group_semvers_storage._attempt_assign_semver(  # pyright: ignore[reportPrivateUsage]
            task_id=task_id,
            similarity_hash=similarity_hash,
            properties_hash=properties_hash,
        )

        # Check the result
        assert result == MajorMinor(major=2, minor=1)
        assert is_new is False

        # Verify no new documents were created
        count = await task_group_semvers_col.count_documents({"task_id": task_id})
        assert count == 1

    async def test_new_minor_version(
        self,
        task_group_semvers_storage: TaskGroupSemverStorage,
        task_group_semvers_col: AsyncCollection,
    ):
        """Test when a document exists with the similarity hash but not the properties hash."""
        task_id = "test_task"
        similarity_hash = "test_hash"
        old_properties_hash = "old_prop_hash"
        new_properties_hash = "new_prop_hash"

        # Insert an existing document
        existing_doc = TaskGroupSemverDocument(
            tenant=TENANT,
            task_id=task_id,
            similarity_hash=similarity_hash,
            major=2,
            max_minor=1,
            minors=[TaskGroupSemverDocument.Minor(minor=1, properties_hash=old_properties_hash)],
        )
        await task_group_semvers_col.insert_one(dump_model(existing_doc))

        # Attempt to assign semver with new properties hash
        result, is_new = await task_group_semvers_storage._attempt_assign_semver(  # pyright: ignore[reportPrivateUsage]
            task_id=task_id,
            similarity_hash=similarity_hash,
            properties_hash=new_properties_hash,
        )

        # Check the result
        assert result == MajorMinor(major=2, minor=2)
        assert is_new is True

        # Verify the document was updated correctly
        doc = await task_group_semvers_col.find_one({"task_id": task_id})
        assert doc is not None
        assert doc["max_minor"] == 2
        assert len(doc["minors"]) == 2
        assert doc["minors"][1]["minor"] == 2
        assert doc["minors"][1]["properties_hash"] == new_properties_hash

    async def test_new_minor_race_condition(
        self,
        task_group_semvers_storage: TaskGroupSemverStorage,
        task_group_semvers_col: AsyncCollection,
    ):
        """Test race condition when creating a new minor version."""
        task_id = "test_task"
        similarity_hash = "test_hash"
        properties_hash = "prop_hash"

        # Insert an existing document
        existing_doc = TaskGroupSemverDocument(
            tenant=TENANT,
            task_id=task_id,
            similarity_hash=similarity_hash,
            major=2,
            max_minor=1,
            minors=[TaskGroupSemverDocument.Minor(minor=1, properties_hash="old_prop_hash")],
        )
        await task_group_semvers_col.insert_one(dump_model(existing_doc))

        # Create two concurrent calls
        async def attempt_assign() -> tuple[MajorMinor, bool]:
            return await task_group_semvers_storage._attempt_assign_semver(  # pyright: ignore[reportPrivateUsage]
                task_id=task_id,
                similarity_hash=similarity_hash,
                properties_hash=properties_hash,
            )

        # Run both calls concurrently
        results = await asyncio.gather(attempt_assign(), attempt_assign(), return_exceptions=True)

        # One call should succeed and one should fail
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        error_count = sum(1 for r in results if isinstance(r, Exception))
        assert success_count == 1, "Expected exactly one successful call"
        assert error_count == 1, "Expected exactly one failed call"

        # Verify only one document was created
        docs = [d async for d in task_group_semvers_col.find({"task_id": task_id})]
        assert len(docs) == 1, "Expected exactly one document to be created"

        # Verify the document has the correct values
        doc = docs[0]
        assert doc["major"] == 2
        assert doc["max_minor"] == 2
        assert doc["similarity_hash"] == similarity_hash
        assert len(doc["minors"]) == 2

    async def test_existing_properties_hash(
        self,
        task_group_semvers_storage: TaskGroupSemverStorage,
        task_group_semvers_col: AsyncCollection,
    ):
        """Test finding an existing version by properties hash."""
        task_id = "test_task"
        similarity_hash = "test_hash"
        properties_hash = "prop_hash"

        # Insert an existing document
        existing_doc = TaskGroupSemverDocument(
            tenant=TENANT,
            task_id=task_id,
            similarity_hash=similarity_hash,
            major=2,
            max_minor=3,
            minors=[
                TaskGroupSemverDocument.Minor(minor=1, properties_hash="old_hash"),
                TaskGroupSemverDocument.Minor(minor=2, properties_hash=properties_hash),
                TaskGroupSemverDocument.Minor(minor=3, properties_hash="newer_hash"),
            ],
        )
        await task_group_semvers_col.insert_one(dump_model(existing_doc))

        # Try to assign a version - should find existing one
        version, is_new = await task_group_semvers_storage._attempt_assign_semver(  # pyright: ignore[reportPrivateUsage]
            task_id=task_id,
            similarity_hash=similarity_hash,
            properties_hash=properties_hash,
        )

        assert version == MajorMinor(major=2, minor=2)
        assert is_new is False

        # Verify no new documents were created
        count = await task_group_semvers_col.count_documents({"task_id": task_id})
        assert count == 1


class TestAssignSemanticVersion:
    async def test_existing_properties_hash(
        self,
        task_group_semvers_storage: TaskGroupSemverStorage,
        task_group_semvers_col: AsyncCollection,
    ):
        """Test finding an existing version by properties hash."""
        task_id = "test_task"
        similarity_hash = "test_hash"
        properties_hash = "prop_hash"

        # Insert an existing document
        existing_doc = TaskGroupSemverDocument(
            tenant=TENANT,
            task_id=task_id,
            similarity_hash=similarity_hash,
            major=2,
            max_minor=3,
            minors=[
                TaskGroupSemverDocument.Minor(minor=1, properties_hash="old_hash"),
                TaskGroupSemverDocument.Minor(minor=2, properties_hash=properties_hash),
                TaskGroupSemverDocument.Minor(minor=3, properties_hash="newer_hash"),
            ],
        )
        await task_group_semvers_col.insert_one(dump_model(existing_doc))

        # Try to assign a version - should find existing one
        version, is_new = await task_group_semvers_storage.assign_semantic_version(
            task_id=task_id,
            # Use a different similarity hash to prove it finds by properties
            similarity_hash="different_hash",
            properties_hash=properties_hash,
        )

        assert version == MajorMinor(major=2, minor=2)
        assert is_new is False

        # Verify no new documents were created
        count = await task_group_semvers_col.count_documents({"task_id": task_id})
        assert count == 1

    async def test_new_version(
        self,
        task_group_semvers_storage: TaskGroupSemverStorage,
        task_group_semvers_col: AsyncCollection,
    ):
        """Test creating a new version when none exists."""
        task_id = "test_task"
        similarity_hash = "test_hash"
        properties_hash = "prop_hash"

        version, is_new = await task_group_semvers_storage.assign_semantic_version(
            task_id=task_id,
            similarity_hash=similarity_hash,
            properties_hash=properties_hash,
        )

        assert version == MajorMinor(major=1, minor=1)
        assert is_new is True

        # Verify document was created correctly
        doc = await task_group_semvers_col.find_one({"task_id": task_id})
        assert doc is not None
        assert doc["major"] == 1
        assert doc["max_minor"] == 1
        assert doc["similarity_hash"] == similarity_hash
        assert len(doc["minors"]) == 1
        assert doc["minors"][0]["minor"] == 1
        assert doc["minors"][0]["properties_hash"] == properties_hash

    async def test_race_condition_all_succeed(
        self,
        task_group_semvers_storage: TaskGroupSemverStorage,
        task_group_semvers_col: AsyncCollection,
    ):
        """Test race condition where all calls eventually succeed through retries."""
        task_id = "test_task"
        similarity_hash = "test_hash"
        properties_hash = "prop_hash"

        # Create concurrent calls
        async def assign_version() -> tuple[MajorMinor, bool]:
            return await task_group_semvers_storage.assign_semantic_version(
                task_id=task_id,
                similarity_hash=similarity_hash,
                properties_hash=properties_hash,
            )

        # Run multiple calls concurrently
        results = await asyncio.gather(
            assign_version(),
            assign_version(),
            assign_version(),
        )

        # All calls should succeed and return the same version
        versions = [version for version, _ in results]
        assert all(v == versions[0] for v in versions)
        assert versions[0] == MajorMinor(major=1, minor=1)

        # At least one should be marked as new
        assert any(is_new for _, is_new in results)

        # Verify only one document was created
        docs = [d async for d in task_group_semvers_col.find({"task_id": task_id})]
        assert len(docs) == 1
        doc = docs[0]
        assert doc["major"] == 1
        assert doc["max_minor"] == 1
        assert len(doc["minors"]) == 1

    async def test_race_condition_existing_doc(
        self,
        task_group_semvers_storage: TaskGroupSemverStorage,
        task_group_semvers_col: AsyncCollection,
    ):
        """Test race condition where document already exists with properties hash."""
        task_id = "test_task"
        similarity_hash = "test_hash"
        properties_hash = "prop_hash"

        # Insert an existing document
        existing_doc = TaskGroupSemverDocument(
            tenant=TENANT,
            task_id=task_id,
            similarity_hash=similarity_hash,
            major=2,
            max_minor=1,
            minors=[TaskGroupSemverDocument.Minor(minor=1, properties_hash=properties_hash)],
        )
        await task_group_semvers_col.insert_one(dump_model(existing_doc))

        # Create concurrent calls
        async def assign_version() -> tuple[MajorMinor, bool]:
            return await task_group_semvers_storage.assign_semantic_version(
                task_id=task_id,
                similarity_hash=similarity_hash,
                properties_hash=properties_hash,
            )

        # Run multiple calls concurrently
        results = await asyncio.gather(
            assign_version(),
            assign_version(),
            assign_version(),
        )

        # All calls should succeed immediately and return the same version
        versions = [version for version, _ in results]
        assert all(v == versions[0] for v in versions)
        assert versions[0] == MajorMinor(major=2, minor=1)

        # None should be marked as new since the version existed
        assert not any(is_new for _, is_new in results)

        # Verify no new documents were created
        count = await task_group_semvers_col.count_documents({"task_id": task_id})
        assert count == 1
