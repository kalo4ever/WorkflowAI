from core.storage.mongo.migrations.base import AbstractMigration


class AddRunFetchIndex(AbstractMigration):
    async def apply(self):
        # Indices that support fetching task runs on the task run endpoint
        basics = [
            ("tenant", 1),
            ("task.id", 1),
            ("task.schema_id", 1),
            ("status", 1),
        ]
        await self._task_runs_collection.create_index(
            [
                *basics,
                ("example_id", 1),
                ("created_at", -1),
            ],
            name="fetch_by_example",
            background=True,
        )
        await self._task_runs_collection.create_index(
            [
                *basics,
                ("group.iteration", 1),
                ("created_at", -1),
            ],
            name="fetch_by_iteration",
            background=True,
        )

    async def rollback(self):
        await self._task_runs_collection.drop_index("fetch_by_example")
        await self._task_runs_collection.drop_index("fetch_by_iteration")
