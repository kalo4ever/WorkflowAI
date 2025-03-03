from pymongo.errors import OperationFailure

from core.storage.mongo.migrations.base import AbstractMigration


class AddTaskRunIndicesMigration(AbstractMigration):
    async def apply(self):
        try:
            await self._task_runs_collection.drop_index("default")
        except OperationFailure:
            pass

        index_base = [
            ("tenant", 1),
            ("task.id", 1),
            ("task.schema_id", 1),
        ]

        # Add status for runs that do not have a status
        await self._task_runs_collection.update_many(
            {"status": {"$exists": False}},
            {"$set": {"status": "success"}},
        )

        # used when fetching cache
        await self._task_runs_collection.create_index(
            [
                *index_base,
                ("group.hash", 1),
                ("task_input_hash", 1),
                ("created_at", -1),
                ("status", 1),
            ],
            name="group_hash_input_hash",
            background=True,
        )

        # used when checking matching runs for evaluations
        await self._task_runs_collection.create_index(
            [
                *index_base,
                ("task_input_hash", 1),
                ("task_output_hash", 1),
                ("created_at", -1),
                ("status", 1),
            ],
            name="input_hash_output_hash",
            background=True,
        )

        # used when aggregating runs for a benchmark
        # The query is also used by the client to fetch newly created
        # runs for a given benchmark (hence the created_at sort)
        await self._task_runs_collection.create_index(
            [
                *index_base,
                ("dataset_benchmark_ids", 1),
                ("created_at", 1),
            ],
            name="dataset_sync",
            partialFilterExpression={"dataset_benchmark_ids": {"$exists": True}},
            background=True,
        )

    async def rollback(self):
        await self._task_runs_collection.drop_index("group_hash_input_hash")
        await self._task_runs_collection.drop_index("input_hash_output_hash")
        await self._task_runs_collection.drop_index("dataset_sync")
