from core.storage.mongo.migrations.base import AbstractMigration


class AddReviewBenchmarkIndicesMigration(AbstractMigration):
    async def apply(self):
        await self._review_benchmarks_collection.create_index(
            [
                ("tenant", 1),
                ("task_id", 1),
                ("task_schema_id", 1),
            ],
            name="by_task_schema_unique",
            unique=True,
            background=True,
        )

    async def rollback(self):
        await self._review_benchmarks_collection.drop_index("by_task_schema_unique")
