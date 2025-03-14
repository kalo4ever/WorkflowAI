from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from api.dependencies.analytics import UserPropertiesDep
from api.dependencies.security import UserOrganizationDep
from api.dependencies.services import AgentSuggestionsServiceDep
from api.dependencies.storage import StorageDep
from api.services.internal_tasks.agent_suggestions_service import SuggestLlmAgentsForCompanyOutputAndStatus
from core.utils.streams import format_model_for_sse

router = APIRouter(prefix="/agents/new-agent")


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
    user_org: UserOrganizationDep,
    agent_suggestions_service: AgentSuggestionsServiceDep,
    storage: StorageDep,
    user_properties: UserPropertiesDep,
) -> StreamingResponse:
    if not user_org:
        raise HTTPException(400, "Can not find organization for user")
    return StreamingResponse(
        (
            format_model_for_sse(chunk)
            async for chunk in agent_suggestions_service.stream_agent_suggestions(
                [],
                user_email=user_properties.user_email,
                storage=storage,
            )
        ),
        media_type="text/event-stream",
    )
