import logging

import pymongo

from core.storage.mongo.migrations.base import AbstractMigration

logger = logging.getLogger(__name__)


class AddTaskDescriptionField(AbstractMigration):
    async def apply(self):
        # Feed the task description with the description from the latest task variant (greatest 'schema_id')
        all_tasks = self._tasks_collection.find({"description": {"$exists": False}})
        async for task in all_tasks:
            task_variant = await self._task_variants_collection.find_one(
                filter={"slug": task["task_id"], "tenant": task["tenant"], "description": {"$exists": True}},
                sort=[("schema_id", pymongo.DESCENDING)],
            )
            if task_variant:
                logger.info(
                    "Updating task with description",
                    extra={"task_id": task["_id"], "description": task_variant["description"]},
                )
                await self._tasks_collection.update_one(
                    {"_id": task["_id"]},
                    {"$set": {"description": task_variant["description"]}},
                )
                continue
            logger.info("No task variant found for task", extra={"task_id": task["_id"]})

    async def rollback(self):
        # NOOP
        pass
