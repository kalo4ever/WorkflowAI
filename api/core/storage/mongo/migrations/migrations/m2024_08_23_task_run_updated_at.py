from pymongo.errors import OperationFailure

from core.storage.mongo.migrations.base import AbstractMigration


class AddTaskRunUpdatedAt(AbstractMigration):
    async def apply(self):
        try:
            await self._task_runs_collection.drop_index("dataset_sync")
        except OperationFailure:
            pass

        await self._task_runs_collection.update_many({}, [{"$set": {"updated_at": "$created_at"}}])

        # used when aggregating runs for a benchmark
        # The query is also used by the client to fetch newly created
        # runs for a given benchmark (hence the created_at sort)
        await self._task_runs_collection.create_index(
            [
                ("tenant", 1),
                ("task.id", 1),
                ("task.schema_id", 1),
                ("dataset_benchmark_ids", 1),
                ("updated_at", 1),
            ],
            name="dataset_sync_updated_at",
            partialFilterExpression={"dataset_benchmark_ids": {"$exists": True}},
            background=True,
        )

    async def rollback(self):
        await self._task_runs_collection.drop_index("dataset_sync_updated_at")
