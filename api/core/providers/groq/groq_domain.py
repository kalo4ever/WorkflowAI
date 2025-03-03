from typing import Literal

from pydantic import BaseModel, Field
from typing_extensions import Annotated

from core.domain.llm_usage import LLMUsage
from core.domain.message import Message
from core.domain.models import Model
from core.providers.base.models import StandardMessage
from core.utils.token_utils import tokens_from_string

GroqRole = Literal["system", "user", "assistant"]


role_to_groq_map: dict[Message.Role, Literal["system", "user", "assistant"]] = {
    Message.Role.SYSTEM: "system",
    Message.Role.USER: "user",
    Message.Role.ASSISTANT: "assistant",
}


class GroqMessage(BaseModel):
    role: GroqRole | None = None
    content: str

    def token_count(self, model: Model) -> int:
        return tokens_from_string(self.content, model)

    @classmethod
    def from_domain(cls, message: Message):
        role = role_to_groq_map[message.role]
        return cls(content=message.content, role=role)

    def to_standard(self) -> StandardMessage:
        return {"role": self.role, "content": self.content}


class JSONResponseFormat(BaseModel):
    type: Literal["json_object"] = "json_object"


class TextResponseFormat(BaseModel):
    type: Literal["text"] = "text"


ResponseFormat = Annotated[
    JSONResponseFormat | TextResponseFormat,
    Field(discriminator="type"),
]


class CompletionRequest(BaseModel):
    temperature: float
    max_tokens: int | None
    model: str
    messages: list[GroqMessage]
    stream: bool
    response_format: ResponseFormat


class _BaseChoice(BaseModel):
    index: int | None = None
    finish_reason: str | None = None


class Choice(_BaseChoice):
    message: GroqMessage


class ChoiceDelta(_BaseChoice):
    class MessageDelta(BaseModel):
        content: str = ""

    delta: MessageDelta


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def to_domain(self) -> LLMUsage:
        return LLMUsage(
            prompt_token_count=self.prompt_tokens,
            completion_token_count=self.completion_tokens,
        )


class CompletionResponse(BaseModel):
    id: str
    choices: list[Choice]
    usage: Usage


class StreamedResponse(BaseModel):
    id: str
    choices: list[ChoiceDelta]
    usage: Usage | None = None

    class XGroq(BaseModel):
        usage: Usage | None = None
        error: str | None = None

    x_groq: XGroq | None = None


class GroqError(BaseModel):
    class Payload(BaseModel):
        message: str | None = None
        type: str | None = None
        param: str | None = None
        code: str = "unknown"

    error: Payload
