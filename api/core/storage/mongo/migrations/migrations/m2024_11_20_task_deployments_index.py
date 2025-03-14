from core.storage.mongo.migrations.base import AbstractMigration


class AddTaskDeploymentsUniqueIndexMigration(AbstractMigration):
    async def apply(self):
        await self._task_deployments_collection.create_index(
            [
                ("tenant", 1),
                ("task_id", 1),
                ("task_schema_id", 1),
                ("environment", 1),
            ],
            name="task_deployments_unique_index",
            unique=True,
            background=True,
        )

    async def rollback(self):
        await self._task_deployments_collection.drop_index("task_deployments_unique_index")
