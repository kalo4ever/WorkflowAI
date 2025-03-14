import workflowai
from pydantic import BaseModel
from workflowai import Model
from workflowai.fields import Image


class DescribeImagesWithContextTaskInput(BaseModel):
    images: list[Image] | None = None
    instructions: str | None = None


class DescribeImagesWithContextTaskOutput(BaseModel):
    image_descriptions: list[str] | None = None


@workflowai.agent(id="describe-images-with-context", model=Model.GEMINI_1_5_FLASH_002)
async def describe_images_with_context(
    input: DescribeImagesWithContextTaskInput,
) -> DescribeImagesWithContextTaskOutput:
    """For each image in the input array, provide a detailed description tailored to the provided instructions. Your output should be an array of strings, where each string contains a textual description of an image that addresses the specific requirements outlined in the instructions, such as:

    - Counting objects
    - Focusing on particular elements

    If the image contains a lot of text, transcribe the image."""
    ...
