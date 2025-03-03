from core.storage.mongo.migrations.base import AbstractMigration


class DeploymentByIterationIdxMigration(AbstractMigration):
    async def apply(self):
        await self._task_deployments_collection.create_index(
            [*self.TASK_PREFIX, ("iteration", 1)],
            name="by_iteration",
        )

    async def rollback(self):
        await self._task_deployments_collection.drop_index("by_iteration")
