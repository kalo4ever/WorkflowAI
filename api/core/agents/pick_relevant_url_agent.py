import workflowai
from pydantic import BaseModel


class PickRelevantUrlAgentsInput(BaseModel):
    class URL(BaseModel):
        index: int | None = None
        url: str | None = None

    num_urls: int | None = None
    url_contents: list[URL] | None = None
    purpose: str | None = None


class PickRelevantUrlAgentsOutput(BaseModel):
    picked_url_indexes: list[int] | None = None


INSTUCTIONS = """You are a specialist at picking the 'num_urls' most relevant URL in a sitemap for a given 'purpose'.
    Based on the 'url', try to infer what are the most relevant URLs for the 'purpose'.
    """


@workflowai.agent(
    id="pick-relevant-url-agents",
    version=workflowai.VersionProperties(
        model=workflowai.Model.GEMINI_2_0_FLASH_001,
        instructions=INSTUCTIONS,
    ),
)
async def pick_relevant_url_agents(
    input: PickRelevantUrlAgentsInput,
) -> PickRelevantUrlAgentsOutput:
    """You are a specialist at picking the 'num_urls' most relevant URL in a sitemap for a given 'purpose'.
    Based on the 'url', try to infer what are the most relevant URLs for the 'purpose'.
    """
    ...
