import asyncio

from bson import ObjectId

from core.domain.errors import DuplicateValueError, InternalError
from core.domain.major_minor import MajorMinor
from core.storage import ObjectNotFoundException, TenantTuple
from core.storage.mongo.models.task_group_semver import TaskGroupSemverDocument
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.base_partial_storage import PartialStorage
from core.storage.mongo.utils import dump_model


class TaskGroupSemverStorage(PartialStorage[TaskGroupSemverDocument]):
    def __init__(self, tenant: TenantTuple, collection: AsyncCollection):
        super().__init__(tenant, collection, TaskGroupSemverDocument)

    async def _insert_new_semver_doc(
        self,
        task_id: str,
        similarity_hash: str,
        properties_hash: str,
    ) -> MajorMinor:
        # First we try and find the latest major doc
        try:
            latest_major_doc = await self._find_one(
                {"task_id": task_id},
                sort=[("major", -1)],
                projection={"_id": 0, "major": 1},
                hint="major_unique",
            )
            latest_major = latest_major_doc.major
        except ObjectNotFoundException:
            latest_major = 0

        new_major = latest_major + 1

        # this will trigger a duplicate key error if the a document with the same similarity hash or major
        # already exists
        await self._insert_one(
            TaskGroupSemverDocument(
                task_id=task_id,
                similarity_hash=similarity_hash,
                major=new_major,
                max_minor=1,
                minors=[TaskGroupSemverDocument.Minor(minor=1, properties_hash=properties_hash)],
            ),
        )
        return MajorMinor(major=new_major, minor=1)

    async def _attempt_assign_semver(
        self,
        task_id: str,
        similarity_hash: str,
        properties_hash: str,
    ) -> tuple[MajorMinor, bool]:
        # First we try to find a semver for the properties hash
        try:
            semver_doc = await self._find_one(
                {"task_id": task_id, "minors.properties_hash": properties_hash},
                hint="properties_hash_unique",
            )
            val = semver_doc.to_semver(properties_hash)
            if not val:
                # This should never happen since we are filtering by properties hash
                raise InternalError("Failed to find semver for properties hash")
            return val, False
        except ObjectNotFoundException:
            pass

        # Maybe a document exists with the similarity hash
        try:
            semver_doc = await self._find_one(
                {"task_id": task_id, "similarity_hash": similarity_hash},
                hint="similarity_unique",
            )
        except ObjectNotFoundException:
            inserted = await self._insert_new_semver_doc(task_id, similarity_hash, properties_hash)
            return inserted, True

        # Then we check if the doc has a minor with the properties hash
        if value := semver_doc.to_semver(properties_hash):
            return value, False

        # Otherwise we create a new minor
        # we use the max minor + 1 as the minor number and use the current max minor as a validator for race conditions
        new_minor = semver_doc.max_minor + 1
        await self._update_one(
            {
                "_id": ObjectId(semver_doc.id),
                "max_minor": semver_doc.max_minor,
            },
            {
                "$set": {"max_minor": new_minor},
                "$push": {
                    "minors": dump_model(
                        TaskGroupSemverDocument.Minor(minor=new_minor, properties_hash=properties_hash),
                    ),
                },
            },
        )

        return MajorMinor(major=semver_doc.major, minor=new_minor), True

    async def assign_semantic_version(
        self,
        task_id: str,
        similarity_hash: str,
        properties_hash: str,
    ):
        # We try 3 times to assign a semver. On race conditions we get either an object not found or a duplicate value
        # error so we just retry
        exc: Exception | None = None
        MAX_RETRIES = 3
        for i in range(0, MAX_RETRIES):
            try:
                return await self._attempt_assign_semver(task_id, similarity_hash, properties_hash)
            except (DuplicateValueError, ObjectNotFoundException) as e:
                if i < MAX_RETRIES - 1:
                    await asyncio.sleep(0.05)
                exc = e
        raise InternalError("Failed to assign semantic version") from exc
