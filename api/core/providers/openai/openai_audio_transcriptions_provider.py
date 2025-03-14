import base64
from io import BytesIO

import httpx
from pydantic import BaseModel


class AudioFileRequest(BaseModel):
    audio_file_data: str
    format: str
    model: str = "whisper-1"

    def to_files(self) -> dict[str, tuple[str, BytesIO, str] | tuple[None, str]]:
        audio_bytes = base64.b64decode(self.audio_file_data)
        audio_buffer = BytesIO(audio_bytes)
        audio_buffer.name = f"audio.{self.format}"
        return {
            "file": (f"audio.{self.format}", audio_buffer, self.format),
            "model": (None, self.model),
        }


class OpenAIAudioTranscriptionsProvider:
    def __init__(self, api_key: str, endpoint: str = "https://api.openai.com/v1/audio/transcriptions"):
        self.api_key = api_key
        self.endpoint = endpoint

    async def transcribe_audio(self, audio_file_data: str, format: str) -> str:
        """
        Transcribe the given audio file using OpenAI's transcription API.

        Args:
            audio_file_data (str): The file data to the audio file.

        Returns:
            str: The transcription result.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        files = AudioFileRequest(audio_file_data=audio_file_data, format=format).to_files()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.endpoint,
                headers=headers,
                files=files,
                # Timeout is added to avoid Timeout errors when the audio file to process is large
                timeout=300.0,  # 5 minutes
            )
            response.raise_for_status()
            return response.json().get("text", "")
