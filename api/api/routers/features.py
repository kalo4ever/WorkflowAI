from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from api.dependencies.event_router import EventRouterDep
from api.dependencies.security import UserDep
from api.dependencies.storage import StorageDep
from api.schemas.models import ModelResponse
from api.services.features import (
    FeatureList,
    FeatureOutputPreview,
    FeatureSchemas,
    FeatureSectionPreview,
    FeatureService,
)
from api.services.models import ModelsService
from core.domain.features import BaseFeature, DirectToAgentBuilderFeature, FeatureWithImage
from core.domain.page import Page
from core.utils.email_utils import safe_domain_from_email
from core.utils.stream_response_utils import safe_streaming_response

router = APIRouter(prefix="/features")


class FeatureSectionResponse(BaseModel):
    sections: list[FeatureSectionPreview] | None = None


@router.get(
    "/sections",
    description="Get the preview of available features sections and tags",
)
async def list_feature_sections(user: UserDep) -> FeatureSectionResponse:
    user_domain = None
    if user is not None:
        # Since user.tenant is not always the user's email domain, we use the email domain to fill the "For You" section
        user_domain = safe_domain_from_email(user.sub)

    return FeatureSectionResponse(sections=await FeatureService.get_feature_sections_preview(user_domain))


class FeatureListResponse(BaseModel):
    features: list[BaseFeature | DirectToAgentBuilderFeature | FeatureWithImage] | None = None


@router.get(
    "/search",
    description="Search for features by tags. Returns a stream with accumulated features.",
    responses={
        200: {
            "content": {
                "text/event-stream": {
                    "schema": FeatureListResponse.model_json_schema(),
                },
            },
        },
    },
)
async def list_features_by_tag(
    user: UserDep,
    tags: str,
) -> StreamingResponse:
    # This endpoint use streaming in order to 1) Have a unified logic with the 'domain' endpoint
    # 2) Be evolutive in case some of the data is dynamically generated in the future.

    async def _stream() -> AsyncIterator[BaseModel]:
        async for features_list in FeatureService.get_features_by_tag(tags):
            yield FeatureListResponse(features=features_list)

    return safe_streaming_response(_stream)


@router.get(
    "/domain/{company_domain}",
    description="Get the features available for a specific company domain",
    responses={
        200: {
            "content": {
                "text/event-stream": {
                    "schema": FeatureList.model_json_schema(),
                },
            },
        },
    },
)
async def list_feature_by_domain(
    user: UserDep,
    storage: StorageDep,
    event_router: EventRouterDep,
    company_domain: str,
) -> StreamingResponse:
    async def _stream() -> AsyncIterator[BaseModel]:
        async for item in FeatureService(storage).get_features_by_domain(company_domain, event_router):
            yield item

    return safe_streaming_response(_stream)


class FeaturePreviewRequest(BaseModel):
    feature: BaseFeature
    company_context: str | None = Field(
        description="To provide for company-specific feature suggestions, null otherwise",
    )


@router.post(
    "/preview",
    description="Get a preview of a feature",
    responses={
        200: {
            "content": {
                "text/event-stream": {
                    "schema": FeatureOutputPreview.model_json_schema(),
                },
            },
        },
    },
)
async def get_feature_preview(
    user: UserDep,
    request: FeaturePreviewRequest,
) -> StreamingResponse:
    async def _stream() -> AsyncIterator[BaseModel]:
        async for chunk in FeatureService().get_agent_preview(
            request.feature.name,
            request.feature.description,
            request.feature.specifications,
            request.company_context,
        ):
            yield chunk

    return safe_streaming_response(_stream)


@router.post(
    "/schemas",
    description="Get the input and output schema for a feature",
)
async def get_feature_schemas(
    user: UserDep,
    request: FeaturePreviewRequest,
) -> FeatureSchemas:
    return await FeatureService().get_agent_schemas(
        request.feature.name,
        request.feature.description,
        request.feature.specifications,
        request.company_context,
    )


@router.get(
    "/models",
    description="Preview available models and their associated data",
)
async def preview_models() -> Page[ModelResponse]:
    models = [ModelResponse.from_service(m) async for m in ModelsService.preview_models() if m.is_default]
    return Page(items=models)
