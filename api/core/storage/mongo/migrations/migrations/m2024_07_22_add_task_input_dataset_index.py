from typing_extensions import override

from core.storage.mongo.migrations.base import AbstractMigration


class AddTaskInputDatasetIndex(AbstractMigration):
    @override
    async def apply(self):
        await self._task_inputs_collection.create_index(
            [("tenant", 1), ("task.id", 1), ("task.schema_id", 1), ("datasets", 1)],
            name="task_input_datasets",
            background=True,
        )

    @override
    async def rollback(self):
        await self._task_inputs_collection.drop_index("task_input_datasets")
