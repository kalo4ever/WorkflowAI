from core.storage.mongo.migrations.base import AbstractMigration


class AddTaskGroupSemversUniqueIndexMigration(AbstractMigration):
    async def _cleanup_changelogs(self):
        duplicates = self._changelogs_collection.aggregate(
            [
                {"$group": {"_id": "$similarity_hash_to", "count": {"$sum": 1}, "doc_ids": {"$push": "$_id"}}},
                {"$match": {"count": {"$gt": 1}}},
            ],
        )
        async for doc in duplicates:
            # delete count -1 records
            await self._changelogs_collection.delete_many({"_id": {"$in": doc["doc_ids"][:-1]}})

    async def apply(self):
        _prefix = ("tenant", 1), ("task_id", 1)

        # Index to prevent duplicate similarity hashes for the same task
        await self._task_group_semvers_collection.create_index(
            [*_prefix, ("similarity_hash", 1)],
            name="similarity_unique",
            unique=True,
        )

        # Index to prevent duplicate major versions for the same task
        await self._task_group_semvers_collection.create_index(
            [*_prefix, ("major", -1)],
            name="major_unique",
            unique=True,
        )

        # Index to prevent duplicate properties hashes for the same task
        await self._task_group_semvers_collection.create_index(
            [*_prefix, ("minors.properties_hash", 1)],
            name="properties_hash_unique",
            unique=True,
        )

        # Index to prevent duplicate major / minor for the same task and
        # improve performance of listing saved versions
        await self._task_run_group_collection.create_index(
            [*_prefix, ("major", -1), ("minor", -1)],
            name="major_minor_unique",
            unique=True,
            partialFilterExpression={"major": {"$exists": True}},
        )

        await self._cleanup_changelogs()
        await self._changelogs_collection.create_index(
            [*_prefix, ("similarity_hash_to", 1)],
            name="similarity_hash_to_unique",
            unique=True,
        )

        await self._changelogs_collection.drop_index("similarity_hash_unique_index")

    async def rollback(self):
        await self._task_group_semvers_collection.drop_index("similarity_unique")
        await self._task_group_semvers_collection.drop_index("major_unique")
        await self._task_group_semvers_collection.drop_index("properties_hash_unique")

        # from m2024_09_24_add_changelogs.py
        await self._changelogs_collection.create_index(
            [("similarity_hash_from", 1), ("similarity_hash_to", 1)],
            name="similarity_hash_unique_index",
            unique=True,  # Enforce uniqueness
            background=True,
        )

        await self._changelogs_collection.drop_index("similarity_hash_to_unique")
