Build agents that can handle multiple modalities, such as images, PDF, documents, audio, and video.

## [Direct link to heading](https://docs.workflowai.com/python-sdk/multimodality\#images)    Images

Add images as input to an agent by using the `Image` class. An image can either have:

- a `content`, base64 encoded data

- a `url`


In the following example, we'll build an agent that can identify the city and country from an image.

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
import base64
import workflowai
from workflowai import Model
from workflowai.fields import Image
from pydantic import BaseModel, Field
from typing import Optional

class ImageInput(BaseModel):
    image: Image = Field(description="The image to analyze")

class ImageOutput(BaseModel):
    city: str = Field(default="", description="Name of the city shown in the image")
    country: str = Field(default="", description="Name of the country where the city is located")
    confidence: Optional[float] = Field(
        default=None,
        description="Confidence level in the identification (0-1)",
    )

@workflowai.agent(id="city-identifier", model=Model.GEMINI_2_0_FLASH_LATEST)
async def identify_city_from_image(image_input: ImageInput) -> ImageOutput:
    """
    Analyze the provided image and identify the city and country shown in it.
    If the image shows a recognizable landmark or cityscape, identify the city and country.
    If uncertain, indicate lower confidence or leave fields empty.

    Focus on:
    - Famous landmarks
    - Distinctive architecture
    - Recognizable skylines
    - Cultural elements that identify the location

    Return empty strings if the city/country cannot be determined with reasonable confidence.
    """
    ...

# Run the agent

## From a remote image
image_url = "https://images.pexels.com/photos/699466/pexels-photo-699466.jpeg"
image = Image(url=image_url)
agent_run = await identify_city_from_image.run(ImageInput(image=image))
print(agent_run)

# Output:
# ==================================================
# {
#   "city": "Paris",
#   "country": "France",
#   "confidence": 1.0
# }
# ==================================================
# Cost: $ 0.00024
# Latency: 6.70s

## From a local image
image_path = "path/to/image.jpg"
with open(image_path, "rb") as image_file:
    content = base64.b64encode(image_file.read()).decode("utf-8")

image = Image(content_type="image/jpeg", data=content)
agent_run = await identify_city_from_image.run(ImageInput(image=image))
```

See a more complete example in [examples/07\_image\_agent.py](https://github.com/WorkflowAI/workflowai-py/blob/main/examples/07_image_agent.py).

You can test this agent with your own images in the WorkflowAI playground. View on [WorkflowAI](https://workflowai.com/docs/agents/city-identifier/1).

![](https://docs.workflowai.com/~gitbook/image?url=https%3A%2F%2F2418444523-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FW4ng0K5LfFjYqHYuPgNh%252Fuploads%252Fgit-blob-190fb9955f6d23e9d4d3ef6efe24fdba2ec698e9%252Fplayground.png%3Falt%3Dmedia&width=768&dpr=4&quality=100&sign=54391a3b&sv=2)

Compare models

Images generation is not supported yet.

## [Direct link to heading](https://docs.workflowai.com/python-sdk/multimodality\#pdf-documents)    PDF, documents

Use the `PDF` class to add PDF, documents, or other files as input to an agent.

In the following example, an agent is created that can answer questions based on a PDF document.

This example uses the `GEMINI_2_0_FLASH_LATEST` model - a powerful and cost-effective multimodal model optimized for processing PDF documents.

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
import workflowai
from pydantic import BaseModel, Field
from workflowai import Model
from workflowai.fields import PDF

class PDFQuestionInput(BaseModel):
    pdf: PDF = Field(description="The PDF document to analyze")
    question: str = Field(description="The question to answer about the PDF content")

class PDFAnswerOutput(BaseModel):
    answer: str = Field(description="The answer to the question based on the PDF content")
    quotes: list[str] = Field(description="Relevant quotes from the PDF that support the answer")

@workflowai.agent(id="pdf-answer-bot", model=Model.GEMINI_2_0_FLASH_LATEST)
async def answer_pdf_question(input: PDFQuestionInput) -> PDFAnswerOutput:
    """
    Analyze the provided PDF document and answer the given question.
    Provide a clear and concise answer based on the content found in the PDF.
    Include relevant quotes to support the answer.
    """
    ...

# Run the agent

## From a remote file
pdf_url = "https://microsoft.gcs-web.com/static-files/b3eef820-6757-44ea-9f98-3963bace4837"
pdf = PDF(url=pdf_url)
agent_run = await answer_pdf_question.run(
    PDFQuestionInput(
        pdf=pdf,
        question="What are the main points from the document?"
    )
)
print(agent_run)

# Output:
# ==================================================
# ==================================================
# {
#   "answer": "This is a SEC Form 4 filing, a Statement of Changes in Beneficial Ownership, for Teri List regarding Microsoft Corporation (MSFT). The document details non-derivative securities acquired and beneficially owned, as well as derivative securities. Teri List has granted power of attorney to Julia Stark, Benjamin O. Orndorff, Michael Pressman, Keith R. Dolliver and Christyne Mayberry.",
#   "quotes": [\
#     "STATEMENT OF CHANGES IN BENEFICIAL OWNERSHIP",\
#     "MICROSOFT CORP [ MSFT]",\
#     "Common Stock",\
#     "Julia Stark, Attorney-in-fact for Teri List",\
#     "I revoke my prior Microsoft Corporation Power of Attorney.",\
#     "The individuals who are authorized to act as my Attorney-In-Fact under this Power of Attorney are as follows:\nJulia Stark\nBenjamin O. Orndorff\nMichael Pressman\nKeith R. Dolliver\nChristyne Mayberry"\
#   ]
# }
# ==================================================
# Cost: $ 0.00033
# Latency: 3.61s

## From a local file

pdf_path = "path/to/pdf.pdf"
with open(pdf_path, "rb") as pdf_file:
    content = pdf_file.read()

pdf = PDF(content_type="application/pdf", data=content)
agent_run = await answer_pdf_question.run(
    PDFQuestionInput(
        pdf=pdf,
        question="What are the main points from the document?"
    )
)
print(agent_run)
```

Try this `pdf-answer-bot` with [your own PDF in the WorkflowAI playground](https://workflowai.com/docs/agents/pdf-answer-bot/1).

## [Direct link to heading](https://docs.workflowai.com/python-sdk/multimodality\#audio)    Audio

Some LLMs can also process audio files directly, without the need to transcribe them first.

First, let's use the `Audio` class to add audio as input to an agent.

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
from workflowai.fields import Audio

class AudioInput(BaseModel):
    audio: Audio = Field()
```

Then, let's create an agent that can detect spam in audio.

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
class AudioOutput(BaseModel):
    is_spam: bool = Field(description="Whether the audio contains spam")
    explanation: str = Field(description="Explanation of the result")

@workflowai.agent(id="audio-spam-detector")
async def detect_audio_spam(input: AudioInput) -> AudioOutput:
    """
    Analyze the provided audio file and determine if it contains spam.
    """
    ...
```

This part of the documentation is not yet complete.

Once the agent is created, you can use `agent.list_models()` to see which models support audio input. Check the `is_not_supported_reason` field to determine if a model supports your multimodal use case:

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
models = await detect_audio_spam.list_models()
# Filter for supported models
supported_models = [model.id for model in models if model.is_not_supported_reason is None]
# Now supported_models contains all models that can process audio
```

Then, you can run the agent with an audio file.

Copy

```inline-grid min-w-full grid-cols-[auto_1fr] p-2 [count-reset:line]
# Run the agent
audio_path = "path/to/audio.mp3"
with open(audio_path, "rb") as audio_file:
    content = audio_file.read()

audio = Audio(content_type="audio/mp3", data=content)
agent_run = await detect_audio_spam.run(
    AudioInput(audio=audio),
    model=Model.GEMINI_2_0_FLASH_LATEST
)
print(agent_run)
```

## [Direct link to heading](https://docs.workflowai.com/python-sdk/multimodality\#video)    Video

Video file as input is not supported yet.

[PreviousVersions](https://docs.workflowai.com/python-sdk/versions) [NextTools](https://docs.workflowai.com/python-sdk/tools)

Last updated 10 days ago

Was this helpful?

* * *