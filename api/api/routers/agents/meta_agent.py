from typing import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from api.dependencies.analytics import UserPropertiesDep
from api.dependencies.event_router import EventRouterDep
from api.dependencies.storage import StorageDep
from api.services.internal_tasks.meta_agent_service import MetaAgentService
from core.domain.fields.chat_message import ChatMessage
from core.utils.stream_response_utils import safe_streaming_response

router = APIRouter(prefix="/agents/meta-agent")


class MetaAgentChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(
        description="The list of messages in the conversation, the last message being the most recent one",
    )


class MetaAgentChatResponse(BaseModel):
    messages: list[ChatMessage] = Field(
        description="The list of messages that compose the response of the meta-agent",
    )


@router.post(
    "/messages",
    description="To chat with WorkflowAI's meta agent",
    responses={
        200: {
            "content": {
                "text/event-stream": {
                    "schema": MetaAgentChatResponse.model_json_schema(),
                },
            },
        },
    },
)
async def get_meta_agent_chat(
    request: MetaAgentChatRequest,
    user_properties: UserPropertiesDep,
    storage: StorageDep,
    event_router: EventRouterDep,
) -> StreamingResponse:
    async def _stream() -> AsyncIterator[BaseModel]:
        meta_agent_service = MetaAgentService(storage=storage, event_router=event_router)

        async for chunk in meta_agent_service.stream_meta_agent_response(
            user_email=user_properties.user_email,
            messages=request.messages,
        ):
            yield MetaAgentChatResponse(messages=chunk)

    return safe_streaming_response(_stream)
