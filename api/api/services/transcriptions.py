import os

import httpx

from core.domain.errors import EntityTooLargeError, InternalError
from core.domain.transcriptions import Transcription
from core.providers.openai.openai_audio_transcriptions_provider import OpenAIAudioTranscriptionsProvider
from core.storage import ObjectNotFoundException
from core.storage.transcription_storage import TranscriptionStorage


class TranscriptionService:
    def __init__(self, storage: TranscriptionStorage):
        self.storage = storage

    async def transcribe_audio(self, file_id: str, data: str, format: str) -> Transcription:
        provider = OpenAIAudioTranscriptionsProvider(api_key=os.environ["OPENAI_API_KEY"])
        try:
            return await self.get_transcription(file_id)
        except ObjectNotFoundException:
            pass

        try:
            transcription = await provider.transcribe_audio(data, format)
            transcription_document = await self.storage.insert_transcription(
                file_id,
                transcription,
                format,
            )
            return transcription_document.to_domain()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 413:
                raise EntityTooLargeError() from e
            raise InternalError("Failed to transcribe audio") from e

    async def get_transcription(self, file_id: str) -> Transcription:
        transcription_document = await self.storage.get_transcription(file_id)
        return Transcription(
            file_id=transcription_document.file_id,
            transcription=transcription_document.transcription,
            format=transcription_document.format,
        )
