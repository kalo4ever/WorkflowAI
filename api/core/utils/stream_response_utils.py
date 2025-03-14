import logging
from collections.abc import AsyncIterator
from typing import AsyncGenerator, Callable

from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from core.domain.errors import DefaultError
from core.utils.streams import format_model_for_sse

_logger = logging.getLogger(__name__)


def safe_streaming_response(
    stream_generator: Callable[[], AsyncIterator[BaseModel]],
    media_type: str = "text/event-stream",
) -> StreamingResponse:
    """
    Creates a StreamingResponse with error handling.

    Args:
        stream_generator: A function that returns an async generator of model objects
        media_type: The media type for the response

    Returns:
        A StreamingResponse object
    """

    async def _stream() -> AsyncGenerator[str, None]:
        try:
            async for item in stream_generator():
                yield format_model_for_sse(item)
        except DefaultError as e:
            if e.capture:
                _logger.exception("Received error during streaming", exc_info=e)
            yield format_model_for_sse(e.error_response())
        except Exception as e:
            _logger.exception("Received unexpected error during streaming", exc_info=e)
            yield format_model_for_sse(DefaultError().error_response())

    return StreamingResponse(
        _stream(),
        media_type=media_type,
    )
