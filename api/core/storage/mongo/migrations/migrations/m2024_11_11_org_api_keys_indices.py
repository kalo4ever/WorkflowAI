from core.storage.mongo.migrations.base import AbstractMigration


class AddOrgAPIKeysIndicesMigration(AbstractMigration):
    async def apply(self):
        await self._organization_collection.create_index(
            [("api_keys.hashed_key", 1)],
            name="org_settings_api_key_index",
            unique=True,
            background=True,
            partialFilterExpression={"api_keys": {"$exists": True}},
        )

        await self._organization_collection.create_index(
            [("api_keys.id", 1)],
            name="org_settings_api_key_id_index",
            unique=True,
            background=True,
            partialFilterExpression={"api_keys": {"$exists": True}},
        )

    async def rollback(self):
        await self._organization_collection.drop_index("org_settings_api_key_index")
        await self._organization_collection.drop_index("org_settings_api_key_id_index")
