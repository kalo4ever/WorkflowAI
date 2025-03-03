import asyncio
import io

from pydub import AudioSegment


def _ffmpeg_format_from_content_type(content_type: str) -> str:
    match content_type:
        case "audio/mpeg":
            return "mp3"
        case _:
            return content_type.split("/")[1]


def _audio_duration_seconds_sync(data: bytes, content_type: str) -> float:
    format = _ffmpeg_format_from_content_type(content_type)
    segment = AudioSegment.from_file(io.BytesIO(data), format)
    return len(segment) / 1000


async def audio_duration_seconds(data: bytes, content_type: str) -> float:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _audio_duration_seconds_sync, data, content_type)
