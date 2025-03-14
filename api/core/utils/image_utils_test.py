import io

from PIL import Image

from core.utils.image_utils import compress_image
from tests.utils import fixture_bytes


def test_compress_b64_image() -> None:
    # Original is 11kb

    raw_image_data = fixture_bytes("files/animal.jpeg")

    compressed_image_data = compress_image(raw_image_data, max_size_kb=4)

    # Test that the compressed image builds with Image.open
    image = Image.open(io.BytesIO(compressed_image_data))  # type: ignore
    image.verify()

    # Test that the compressed image is smaller than the 4kb
    assert len(compressed_image_data) < 4 * 1024


def test_do_not_compress_when_already_below_max_size() -> None:
    # Original is 11kb
    raw_image_data = fixture_bytes("files/animal.jpeg")

    compressed_image_data = compress_image(raw_image_data, max_size_kb=15)

    assert compressed_image_data == compressed_image_data
