from core.storage.mongo.migrations.base import AbstractMigration


class InputEvaluationsIndexMigration(AbstractMigration):
    async def apply(self):
        # Index so that we can get the latest input evaluation for a task and input hash
        await self._input_evaluations_collection.create_index(
            [("tenant", 1), ("task_id", 1), ("task_schema_id", 1), ("input_hash", 1), ("_id", -1)],
            name="fetch_latest_input_evaluation",
            background=True,
        )

    async def rollback(self):
        await self._input_evaluations_collection.drop_index("fetch_latest_input_evaluation")
