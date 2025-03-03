from core.storage.mongo.migrations.base import AbstractMigration


class AddTaskNamesMigration(AbstractMigration):
    async def apply(self):
        # Create an instance in task_info collection for each task

        all_taskids_with_names = self._task_variants_collection.aggregate(
            [
                {
                    "$group": {
                        "_id": {
                            "task_id": "$slug",
                            "tenant": "$tenant",
                        },
                        "name": {"$first": "$name"},
                    },
                },
            ],
        )

        async for task in all_taskids_with_names:
            await self._tasks_collection.update_one(
                {
                    "task_id": task["_id"]["task_id"],
                    "tenant": task["_id"]["tenant"],
                },
                {
                    "$set": {
                        "name": task["name"],
                    },
                },
                upsert=True,
            )

    async def rollback(self):
        # NOOP
        pass
