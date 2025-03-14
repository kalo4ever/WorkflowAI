from core.storage.mongo.migrations.base import AbstractMigration


class AddTaskRunInputOutputHashesIndexMigration(AbstractMigration):
    async def apply(self):
        await self._task_runs_collection.create_index(
            [
                ("tenant", 1),
                ("task.id", 1),
                ("task.schema_id", 1),
                ("task_input_hash", 1),
                ("task_output_hash", 1),
                # We add group iteration to efficiently fetch the unique iterations for a given input/output pair
                ("group.iteration", 1),
            ],
            name="input_output_hashes",
            background=True,
        )

    async def rollback(self):
        await self._task_runs_collection.drop_index("input_output_hashes")
