import workflowai
from pydantic import BaseModel, Field

from core.agents.company_agent_suggestion_agent import CompanyContext
from core.domain.features import BaseFeature


class GenerateAIRoadmapPresentationInput(BaseModel):
    roadmap_agents: list[BaseFeature] | None = Field(
        default=None,
        description="List of the agent that are in the company's AI roadmap",
    )

    company_context: CompanyContext | None = Field(
        default=None,
        description="The context of the company to generate the roadmap presentation for",
    )


class GenerateAIRoadmapPresentationOutput(BaseModel):
    roadmap_presentation: str | None = Field(
        default=None,
        description="A formatted presentation of the AI roadmap",
    )


INSTRUCTIONS = """You are an AI Roadmap Strategist. Your job is to generate an inspiring and visionary AI roadmap summary. The summary should integrate the provided company context with the list of AI features, emphasizing how these features can be strategically implemented to drive innovation, growth, and competitive advantage.

Instructions:
- Use the company context details (e.g., industry focus, company size, strategic goals) to highlight the organization’s unique strengths and areas for opportunity.
- Incorporate the list of AI features to illustrate tangible benefits and a clear path toward implementation. Only use the 4-6 features that seem most transformative for the company.
- Ensure the tone is visionary, motivational, and actionable.
- The summary must offer a clear narrative of how AI can transform the organization.
- Use emojis to make the content more engaging.
- IMPORTANT: the presentation should not only list features but create a compelling narrative that ignites enthusiasm and guides actionable next steps.
- IMPORTANT: You MUST use double line breaks to separate paragraphs and make the content more readable.
- The presentation must be max 25 lines so you need to focus on the most transformative features.
- You can use "... AI" (ex: Google AI, Salesforce AI, etc.), to talk about the artificial intelligence of the company.
"""


@workflowai.agent(
    id="ai-roadmap-presentation",
    version=workflowai.VersionProperties(
        model=workflowai.Model.CLAUDE_3_7_SONNET_20250219,
        instructions=INSTRUCTIONS,
        temperature=0.7,  # Higher temperature for more creative and engaging presentations
    ),
)
async def generate_ai_roadmap_presentation(
    input: GenerateAIRoadmapPresentationInput,
) -> GenerateAIRoadmapPresentationOutput: ...
