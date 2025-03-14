from core.storage.mongo.migrations.base import AbstractMigration


class CreateChangelogsCollectionMigration(AbstractMigration):
    async def apply(self):
        # Create a non-unique index for tenant, task_id, and task_schema_id
        await self._changelogs_collection.create_index(
            [("tenant", 1), ("task_id", 1), ("task_schema_id", 1)],
            name="tenant_task_id_task_schema_id_index",
            background=True,
        )

        # Ensure the unique index on similarity_hash_from and similarity_hash_to remains
        await self._changelogs_collection.create_index(
            [("similarity_hash_from", 1), ("similarity_hash_to", 1)],
            name="similarity_hash_unique_index",
            unique=True,  # Enforce uniqueness
            background=True,
        )

    async def rollback(self):
        # Rollback non-unique index for tenant, task_id, and task_schema_id
        await self._changelogs_collection.drop_index("tenant_task_id_task_schema_id_index")

        # Rollback for similarity_hash_from and similarity_hash_to unique index
        await self._changelogs_collection.drop_index("similarity_hash_unique_index")
