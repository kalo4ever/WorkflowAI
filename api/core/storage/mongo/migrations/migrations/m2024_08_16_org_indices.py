from core.storage.mongo.migrations.base import AbstractMigration


class AddOrgIndicesMigration(AbstractMigration):
    async def apply(self):
        await self._organization_collection.create_index(
            [("slug", 1)],
            name="org_settings_slug_index",
            unique=True,
            partialFilterExpression={"slug": {"$exists": True}},
            background=True,
        )

        await self._organization_collection.create_index(
            [("domain", 1)],
            name="org_settings_domain_index",
            unique=True,
            partialFilterExpression={"domain": {"$exists": True}},
            background=True,
        )

        await self._organization_collection.create_index(
            [("org_id", 1)],
            name="org_settings_org_id_index",
            unique=True,
            partialFilterExpression={"org_id": {"$exists": True}},
            background=True,
        )

    async def rollback(self):
        await self._organization_collection.drop_index("org_settings_slug_index")
        await self._organization_collection.drop_index("org_settings_domain_index")
        await self._organization_collection.drop_index("org_settings_org_id_index")
