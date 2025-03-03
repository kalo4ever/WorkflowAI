from core.storage.mongo.migrations.base import AbstractMigration


class OrgSettingsIndicesMigration(AbstractMigration):
    async def apply(self):
        # Making sure only one tenant can exist for a given owner_id if it doesn't have an org_id
        await self._organization_collection.create_index(
            [
                ("owner_id", 1),
                # We make the index unique by org_id as well
                # This will ensure that an owner id:
                # - can not have two tenants that do not have an org_id
                # - can create multiple organizations
                ("org_id", 1),
            ],
            name="unique_owner_id",
            unique=True,
            partialFilterExpression={"owner_id": {"$exists": True}},
        )

        await self._organization_collection.create_index(
            [
                ("anonymous_user_id", 1),
                # We make the index unique by user_id as well
                # This will ensure that an owner id:
                # - can not have two tenants that do not have an user_id
                # - a user that logs out with the same anonymous tenant can still view stuff while unauthenticated
                ("user_id", 1),
            ],
            name="anonymous_user_id_and_user_id_unique",
            unique=True,
            partialFilterExpression={"anonymous_user_id": {"$exists": True}, "user_id": {"$exists": True}},
        )
        await self._organization_collection.drop_index("anonymous_user_id_unique")

        # Replacing the old uid unique index since it was partial
        await self._organization_collection.create_index(
            [
                ("uid", 1),
            ],
            name="uid_unique_final",
            unique=True,
        )

        await self._organization_collection.drop_index("uid_unique")

        await self._tasks_collection.create_index(
            [
                ("uid", 1),
            ],
            name="uid_unique_final",
            unique=True,
        )
        await self._tasks_collection.drop_index("uid_unique")

    async def rollback(self):
        await self._organization_collection.drop_index("unique_owner_id")
        await self._organization_collection.drop_index("uid_unique_final")
        await self._tasks_collection.drop_index("uid_unique_final")

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

        await self._organization_collection.create_index(
            [
                ("anonymous_user_id", 1),
            ],
            name="anonymous_user_id_unique",
            background=True,
            unique=True,
            partialFilterExpression={"anonymous_user_id": {"$exists": True}},
        )
