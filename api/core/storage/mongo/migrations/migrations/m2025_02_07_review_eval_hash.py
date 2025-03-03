from core.storage.mongo.migrations.base import AbstractMigration


class AddReviewEvalHashIndexMigration(AbstractMigration):
    async def apply(self):
        await self._reviews_collection.create_index(
            [
                ("tenant", 1),
                ("task_id", 1),
                ("task_schema_id", 1),
                ("eval_hash", 1),
                # Ordering by reviewer type so that user reviews are preferred
                ("reviewer.type", -1),
            ],
            name="eval_hash",
            partialFilterExpression={"is_stale": False},
        )

        await self._reviews_collection.create_index(
            [
                ("tenant", 1),
                ("task_id", 1),
                # Ordering by reviewer type so that user reviews are preferred
                ("reviewer.type", -1),
                ("outcome", 1),
                ("eval_hash", 1),
            ],
            name="outcome_to_eval_hash",
            partialFilterExpression={"is_stale": False},
        )

        await self._reviews_collection.create_index(
            [
                ("tenant", 1),
                ("task_id", 1),
                ("task_schema_id", 1),
                ("task_input_hash", 1),
                ("task_output_hash", 1),
                ("reviewer.evaluator_id", 1),
                ("reviewer.input_evaluation_id", 1),
            ],
            name="ai_reviews_unique",
            unique=True,
            partialFilterExpression={
                "reviewer.reviewer_type": "ai",
            },
        )

    async def rollback(self):
        await self._reviews_collection.drop_index("eval_hash")
