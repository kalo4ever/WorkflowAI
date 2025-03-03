import base64
import os
from typing import Literal

from fastapi import APIRouter
from openai import AsyncOpenAI

router = APIRouter(prefix="/images")


async def generate_and_display_image(
    prompt: str, size: Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"],
) -> bytes:
    # Initialize the AsyncOpenAI client
    client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

    # Generate an image using DALL-E, requesting base64 data
    response = await client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality="hd",
        n=1,
        response_format="b64_json",
    )

    # Get the base64 image data from the response
    return base64.b64decode(response.data[0].b64_json)  # type: ignore

