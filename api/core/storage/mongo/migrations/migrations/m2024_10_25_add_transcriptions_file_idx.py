from typing_extensions import override

from core.storage.mongo.migrations.base import AbstractMigration


class AddTranscriptionsFileIdIndexMigration(AbstractMigration):
    @override
    async def apply(self):
        # Create index for efficient querying by file_id within tenant
        await self._transcriptions_collection.create_index(
            [("tenant", 1), ("file_id", 1)],
            name="transcriptions_by_file_id",
            unique=True,
            background=True,
        )

    @override
    async def rollback(self):
        await self._transcriptions_collection.drop_index("transcriptions_by_file_id")
