from pydantic import BaseModel


class Transcription(BaseModel):
    file_id: str
    transcription: str
    format: str
