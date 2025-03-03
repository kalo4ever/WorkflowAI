import base64
import imghdr
from typing import Literal

from core.domain.errors import InvalidFileError


def extract_text_from_file_base64(base64_data: str) -> str:
    """
    Extract text content from a base64 encoded file.

    Args:
        base64_data (str): The base64 encoded file content.
        mime_type (TextFileMimeType): The MIME type of the file.

    Returns:
        str: The extracted text content of the file.

    Raises:
        ValueError: If an unsupported MIME type is provided.
    """
    if base64_data == "":
        return ""

    try:
        decoded_bytes = base64.b64decode(base64_data)
    except ValueError as e:
        raise InvalidFileError(f"Invalid base64 data: {e}")

    try:
        return decoded_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
        raise InvalidFileError(f"Invalid unicode data: {e}")


file_signatures = signatures = {
    # Images
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"GIF87a": "image/gif",
    b"GIF89a": "image/gif",
    b"BM": "image/bmp",
    b"II*\x00": "image/tiff",
    b"MM\x00*": "image/tiff",
    # Documents
    b"%PDF": "application/pdf",
    # Audio
    b"ID3": "audio/mpeg",
    b"\xff\xfb": "audio/mpeg",
    b"\xff\xf3": "audio/mpeg",
    b"\xff\xf2": "audio/mpeg",
}


def guess_content_type(file_data: bytes, mode: Literal["image", "audio", "video"] | None = None) -> str | None:
    for signature, mime_type in file_signatures.items():
        if file_data.startswith(signature):
            return mime_type

    if file_data.startswith(b"RIFF"):
        if file_data[8:12] == b"WEBP":
            return "image/webp"
        if b"WAVE" in file_data[:12]:
            return "audio/wav"

    # If we are in image mode, we first try and use the internal lib
    if mode == "image" or mode is None:
        try:
            image_type = imghdr.what(None, h=file_data)
            if image_type:
                return f"image/{image_type}"
        except Exception:
            pass

    return None
