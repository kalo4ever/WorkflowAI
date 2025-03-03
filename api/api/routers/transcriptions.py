from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from api.dependencies.services import TranscriptionServiceDep

router = APIRouter(prefix="/transcriptions")


class TranscriptionResponse(BaseModel):
    transcription: str


AudioFormat = Literal["m4a", "mp3", "webm", "mp4", "mpga", "wav", "mpeg"]
# openai audio transcription has 25MB per file limit


class FileInputRequest(BaseModel):
    file_id: str
    data: str  # holds base 64 encoded audio file
    format: AudioFormat


@router.post("", response_model=TranscriptionResponse, description="Transcribe audio")
async def transcribe_audio(
    transcription_service: TranscriptionServiceDep,
    input_req: FileInputRequest,
) -> TranscriptionResponse:
    # Endpoint : POST /transcriptions
    transcription = await transcription_service.transcribe_audio(
        input_req.file_id,
        input_req.data,
        input_req.format,
    )
    return TranscriptionResponse(transcription=transcription.transcription)


@router.get("/{file_id}", response_model=TranscriptionResponse, description="Get Transcription")
async def get_transcription(
    file_id: str,
    transcription_service: TranscriptionServiceDep,
) -> TranscriptionResponse:
    # Endpoint : GET /transcriptions/{file_id}
    # If transcription with file_id exists, return it
    transcription = await transcription_service.get_transcription(file_id)
    return TranscriptionResponse(transcription=transcription.transcription)
