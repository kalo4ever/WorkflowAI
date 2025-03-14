from core.storage.mongo.migrations.base import AbstractMigration


class AddTaskRunByModelIndexMigration(AbstractMigration):
    async def apply(self):
        await self._task_runs_collection.create_index(
            [
                ("tenant", 1),
                ("task.id", 1),
                ("task.schema_id", 1),
                ("group.properties.model", 1),
                ("created_at", -1),
            ],
            name="task_run_by_group_properties_model",
            background=True,
        )

    async def rollback(self):
        await self._task_runs_collection.drop_index("task_run_by_group_properties_model")
