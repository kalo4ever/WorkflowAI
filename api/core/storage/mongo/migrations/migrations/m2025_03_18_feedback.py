from typing import override

from core.storage.mongo.migrations.base import AbstractMigration


class FeedbackIndicesMigration(AbstractMigration):
    @override
    async def apply(self):
        await self._feedback_collection.create_index(
            [
                ("tenant_uid", 1),
                ("task_uid", 1),
                ("run_id", 1),
                ("user_id", 1),
            ],
            unique=True,
            partialFilterExpression={"is_stale": False},
            name="unique_by_user_id",
        )

        await self._feedback_collection.create_index(
            [
                ("tenant_uid", 1),
                ("task_uid", 1),
                ("run_id", 1),
                ("_id", -1),
            ],
            name="by_run_id",
        )

        await self._feedback_collection.create_index(
            [
                ("tenant_uid", 1),
                ("task_uid", 1),
                ("_id", -1),
            ],
            name="by_task_uid",
        )

    @override
    async def rollback(self):
        await self._feedback_collection.drop_index("unique_by_user_id")
        await self._feedback_collection.drop_index("by_run_id")
        await self._feedback_collection.drop_index("by_task_uid")
