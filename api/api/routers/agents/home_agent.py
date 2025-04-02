from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from api.dependencies.services import AgentSuggestionsServiceDep
from api.services.internal_tasks.agent_suggestions_service import (
    SuggestedAgentOutputExampleOutputWithSchema,
    SuggestLlmAgentsForCompanyOutputAndStatus,
)
from core.agents.suggest_llm_features_for_company_agent import (
    AgentSuggestionChatMessage,
    SuggestedAgent,
)
from core.utils.streams import format_model_for_sse

router = APIRouter(prefix="/agents/home", include_in_schema=False)


class TaskSuggestionChatRequest(BaseModel):
    messages: list[AgentSuggestionChatMessage] = Field(
        description="The list of previous messages in the conversation, the last message is the most recent one",
    )


@router.post(
    "/messages",
    description="Allows to chat with an assistant and get agent suggestions",
    responses={
        200: {
            "content": {
                "application/json": {
                    "schema": SuggestLlmAgentsForCompanyOutputAndStatus.model_json_schema(),
                },
                "text/event-stream": {
                    "schema": SuggestLlmAgentsForCompanyOutputAndStatus.model_json_schema(),
                },
            },
        },
    },
)
async def get_agent_suggestion_chat(
    request: TaskSuggestionChatRequest,
    agent_suggestions_service: AgentSuggestionsServiceDep,
) -> StreamingResponse:
    return StreamingResponse(
        (
            format_model_for_sse(chunk)
            async for chunk in agent_suggestions_service.stream_agent_suggestions(
                request.messages,
                storage=None,  # No storage available, since user is not authenticated
            )
        ),
        media_type="text/event-stream",
    )


class AgentSuggestionPreviewRequest(BaseModel):
    suggested_agent: SuggestedAgent = Field(
        description="The agent suggestion to generate output preview for",
    )


@router.post(
    "/agents/preview",
    description="Preview an agent suggestion's output",
    responses={
        200: {
            "content": {
                "application/json": {
                    "schema": SuggestedAgentOutputExampleOutputWithSchema.model_json_schema(),
                },
                "text/event-stream": {
                    "schema": SuggestedAgentOutputExampleOutputWithSchema.model_json_schema(),
                },
            },
        },
    },
)
async def get_agent_suggestion_preview(
    request: AgentSuggestionPreviewRequest,
    agent_suggestions_service: AgentSuggestionsServiceDep,
) -> StreamingResponse:
    return StreamingResponse(
        (
            format_model_for_sse(chunk)
            async for chunk in agent_suggestions_service.stream_agent_output_preview(
                request.suggested_agent,
            )
        ),
        media_type="text/event-stream",
    )
