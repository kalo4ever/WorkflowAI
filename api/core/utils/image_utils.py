import io

from PIL import Image


def compress_image(image_bytes: bytes, max_size_kb: int = 600) -> bytes:
    image_size_bytes = len(image_bytes)
    max_size_bytes = max_size_kb * 1024

    # Check if the original image size is already within the limit
    if image_size_bytes <= max_size_bytes:
        return image_bytes

    # Convert bytes to PIL image
    image = Image.open(io.BytesIO(image_bytes))  # type: ignore

    # Initialize variables
    quality = 90
    decrement_step = 20
    min_quality = 10

    while quality >= min_quality:
        # Convert image to bytes with current quality
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=quality)  # type: ignore
        image_bytes = buffered.getvalue()
        image_size_bytes = len(image_bytes)

        # Check if the image size is within the limit
        if image_size_bytes <= max_size_bytes:
            return image_bytes

        # Decrease the quality for the next iteration
        quality -= decrement_step

        image = Image.open(io.BytesIO(image_bytes))  # type: ignore

    # If the loop ends without finding a satisfactory compression, return the last attempt
    return image_bytes
