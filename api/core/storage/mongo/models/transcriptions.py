from core.domain.transcriptions import Transcription
from core.storage.mongo.models.base_document import BaseDocumentWithID


class TranscriptionDocument(BaseDocumentWithID):
    file_id: str
    transcription: str
    format: str

    @classmethod
    def from_domain(cls, file_id: str, transcription: str, format: str):
        return cls(file_id=file_id, transcription=transcription, format=format)

    def to_domain(self) -> Transcription:
        return Transcription(
            file_id=self.file_id,
            transcription=self.transcription,
            format=self.format,
        )
