from core.storage.mongo.migrations.base import AbstractMigration


class AddUniqueIdsMigration(AbstractMigration):
    """Add unique ids to tenants and tasks"""

    async def apply(self):
        # UID is meant to be a unique UInt32 identifier
        await self._organization_collection.create_index(
            [
                ("uid", 1),
            ],
            name="uid_unique",
            unique=True,
            partialFilterExpression={"uid": {"$exists": True}},
        )

        await self._tasks_collection.create_index(
            [
                ("uid", 1),
            ],
            name="uid_unique",
            unique=True,
            partialFilterExpression={"uid": {"$exists": True}},
        )

    async def rollback(self):
        await self._organization_collection.drop_index("uid_unique")
        await self._tasks_collection.drop_index("uid_unique")
