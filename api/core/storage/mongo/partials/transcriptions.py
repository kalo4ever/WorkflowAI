from core.storage import TenantTuple
from core.storage.mongo.models.transcriptions import TranscriptionDocument
from core.storage.mongo.mongo_types import AsyncCollection
from core.storage.mongo.partials.base_partial_storage import PartialStorage


class MongoTranscriptionStorage(PartialStorage[TranscriptionDocument]):
    def __init__(self, tenant: TenantTuple, collection: AsyncCollection):
        super().__init__(tenant, collection, TranscriptionDocument)

    async def insert_transcription(
        self,
        file_id: str,
        transcription: str,
        format: str,
    ) -> TranscriptionDocument:
        return await self._insert_one(TranscriptionDocument.from_domain(file_id, transcription, format))

    async def get_transcription(self, file_id: str) -> TranscriptionDocument:
        return await self._find_one({"file_id": file_id})
