from core.storage.mongo.migrations.base import AbstractMigration


class AddTaskRunByHashWithScoresIndexMigration(AbstractMigration):
    async def apply(self):
        # Create a non-unique index for tenant, task_id, and task_schema_id
        await self._task_runs_collection.create_index(
            [
                ("tenant", 1),
                ("task.id", 1),
                ("task.schema_id", 1),
                ("task_input_hash", 1),
                ("task_output_hash", 1),
                ("created_at", -1),
            ],
            name="task_run_by_hash_with_scores",
            background=True,
            partialFilterExpression={"scores.0": {"$exists": True}, "status": "success"},
        )
        # Deleting previous index
        await self._task_runs_collection.drop_index("input_hash_output_hash")

    async def rollback(self):
        await self._task_runs_collection.drop_index("task_run_by_hash_with_scores")

        # Recreate old index
        await self._task_runs_collection.create_index(
            [
                ("tenant", 1),
                ("task.id", 1),
                ("task.schema_id", 1),
                ("task_input_hash", 1),
                ("task_output_hash", 1),
                ("created_at", -1),
                ("status", 1),
            ],
            name="input_hash_output_hash",
            background=True,
        )
