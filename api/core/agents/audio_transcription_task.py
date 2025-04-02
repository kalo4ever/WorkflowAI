# Install the SDK

from pydantic import BaseModel, Field

from core.domain.deprecated.task import Task
from core.domain.fields.file import File


class AudioTranscriptionTaskInput(BaseModel):
    audio_file: File = Field(description="The audio file to transcribe", json_schema_extra={"format": "audio"})


class AudioTranscriptionTaskOutput(BaseModel):
    transcription: str = Field(description="The transcription of the audio file")


# This is a task that transcribes an audio file, It could not yet be built by WorkflowAI
# as the format is not yet supported by the frontend/SDK
# https://linear.app/workflowai/issue/WOR-1774/ux-audio-file-inputs
class AudioTranscriptionTask(Task[AudioTranscriptionTaskInput, AudioTranscriptionTaskOutput]):
    input_class: type[AudioTranscriptionTaskInput] = AudioTranscriptionTaskInput
    output_class: type[AudioTranscriptionTaskOutput] = AudioTranscriptionTaskOutput
    instructions: str = """Transcribe the audio file. If the audio is not clear, do your best effort to transcribe it.
Transcribe in the original language of speech if possible. If the language cannot be determined or transcribed accurately,
default to transcribing in English. Pauses in speech should be transcribed as '...'.
Capture the speaker's tone, intent and emotions e.x. exclamations and other intonations that convey emotion.
"""
