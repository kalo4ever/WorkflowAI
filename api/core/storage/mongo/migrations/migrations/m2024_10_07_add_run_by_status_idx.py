from core.storage.mongo.migrations.base import AbstractMigration


class AddTaskRunByStatusIndexMigration(AbstractMigration):
    async def apply(self):
        # Create a non-unique index for tenant, task_id, and task_schema_id
        await self._task_runs_collection.create_index(
            [
                ("tenant", 1),
                ("task.id", 1),
                ("task.schema_id", 1),
                ("status", 1),
                ("created_at", -1),
            ],
            name="task_run_by_status",
            background=True,
        )

    async def rollback(self):
        await self._task_runs_collection.drop_index("task_run_by_status")
