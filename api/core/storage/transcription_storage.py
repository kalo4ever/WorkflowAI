from typing import Protocol

from core.storage.mongo.models.transcriptions import TranscriptionDocument


class TranscriptionStorage(Protocol):
    async def insert_transcription(
        self,
        file_id: str,
        transcription: str,
        format: str,
    ) -> TranscriptionDocument: ...

    async def get_transcription(self, file_id: str) -> TranscriptionDocument: ...
