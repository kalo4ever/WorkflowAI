from core.storage.mongo.migrations.base import AbstractMigration


class AddReviewsNonStaleIndexMigration(AbstractMigration):
    async def apply(self):
        await self._reviews_collection.create_index(
            [
                ("tenant", 1),
                ("task_id", 1),
                ("task_schema_id", 1),
                ("task_input_hash", 1),
                ("task_output_hash", 1),
                # sort by id in descending order to make sure the most recent reviews are returned first
                ("_id", -1),
            ],
            name="reviews_non_stale_index",
            background=True,
            partialFilterExpression={"is_stale": False},
        )

    async def rollback(self):
        await self._reviews_collection.drop_index("reviews_non_stale_index")
