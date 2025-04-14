import workflowai
from pydantic import BaseModel, Field


class UptimeExtractorAgentInput(BaseModel):
    status_page_content: str | None = Field(
        default=None,
        description="The content of the status page to extract the uptime from",
    )

    extraction_instructions: str | None = Field(
        default=None,
        description="Additional instructions to help the agent extract the right uptime from the status page",
    )


class UptimeExtractorAgentOutput(BaseModel):
    uptime: float | None = Field(
        ge=0,
        le=100,
        description="The uptime extracted from the status page, between 0 and 100. All decimals from the status page must be extracted.",
        default=None,
    )
    since: str | None = Field(
        default=None,
        description="The start date of the uptime extraction period, in ISO 8601 format: YYYY-MM-DD",
    )


@workflowai.agent(
    id="uptime-extraction-agent",
    version=workflowai.VersionProperties(
        model=workflowai.Model.GEMINI_2_0_FLASH_001,
    ),
)
async def uptime_extraction_agent(input: UptimeExtractorAgentInput) -> workflowai.Run[UptimeExtractorAgentOutput]:
    """You are a specialist at extracting uptime values from status pages. You must extract the uptime from the 'status_page_content', and also take the eventual 'extraction_instructions' into account."""
    ...
