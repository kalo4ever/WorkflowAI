from core.storage.mongo.migrations.base import AbstractMigration


class AddAnonymousUserIdUniqueIndexMigration(AbstractMigration):
    async def apply(self):
        await self._organization_collection.create_index(
            [
                ("anonymous_user_id", 1),
            ],
            name="anonymous_user_id_unique",
            background=True,
            unique=True,
            partialFilterExpression={"anonymous_user_id": {"$exists": True}},
        )

    async def rollback(self):
        await self._organization_collection.drop_index("anonymous_user_id_index")
