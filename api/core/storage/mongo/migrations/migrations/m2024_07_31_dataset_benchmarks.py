from core.storage.mongo.migrations.base import AbstractMigration


class DatasetBenchmarksMigration(AbstractMigration):
    async def apply(self):
        await self._dataset_benchmarks_collection.create_index(
            [("task_id", 1), ("task_schema_id", 1), ("dataset_id", 1), ("tenant", 1)],
            name="dataset_benchmark_unique",
            unique=True,
            background=True,
        )

    async def rollback(self):
        await self._dataset_benchmarks_collection.drop_index("dataset_benchmark_unique")
