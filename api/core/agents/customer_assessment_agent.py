import workflowai
from pydantic import BaseModel, Field

from core.domain.url_content import URLContent


class CustomerAssessementAgentInput(BaseModel):
    main_company_domain: str
    url_contents: list[URLContent]


class CustomerAssessementAgentOutput(BaseModel):
    company_name: str | None = Field(
        default=None,
        description="The name of the company",
    )
    company_website_url: str | None = Field(
        default=None,
        description="The website URL of the company",
    )
    company_linkedin_url: str | None = Field(
        default=None,
        description="The LinkedIn URL of the company",
    )
    company_industry: str | None = Field(
        default=None,
        description="The precise industry of the company",
        examples=["AI Saas", "Fintech", "Food & Beverages"],
    )
    company_funding_million_usd: float | None = Field(
        default=None,
        description="The amount of funding the company has raised in millions of USD",
    )
    company_annual_revenue_millions_usd: float | None = Field(
        default=None,
        description="The annual revenue of the company in millions of USD",
    )
    company_employees_count: int | None = Field(
        default=None,
        description="The number of employees in the company",
    )
    founded_year: int | None = Field(
        default=None,
        description="The year the company was founded",
    )
    locations: list[str] | None = Field(
        default=None,
        description="The locations of the company",
    )
    summary: str | None = Field(
        default=None,
        description="A summary of the company context is size, products, funding history, revenues, etc",
    )


@workflowai.agent(
    version=workflowai.VersionProperties(
        model=workflowai.Model.GEMINI_2_0_FLASH_001,
    ),
)
async def customer_assessement_agent(input: CustomerAssessementAgentInput) -> CustomerAssessementAgentOutput:
    """You are a market research specialist. Your goal is to fill the output based on all the URL content passed in input and only based on the URL content. When not sure, it's better that you leave fields empty rather than trying to guess."""
    ...
