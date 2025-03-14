from enum import Enum

import workflowai
from pydantic import BaseModel, Field
from workflowai import Model


class ClassifyEmailDomainAgentInput(BaseModel):
    email_domain: str | None = None


class ClassifyEmailDomainAgentOutput(BaseModel):
    class Result(Enum):
        INVALID_DOMAIN = "invalid_domain"
        PERSONAL_EMAIL_DOMAIN = "personal_email_domain"
        COMPANY_EMAIL_DOMAIN = "company_email_domain"

    result: Result = Field(
        description="Wether the email domain is an invalid domain, a personal email domain or a company email domain",
    )


@workflowai.agent(id="classify-email-domain", model=Model.GPT_4O_MINI_LATEST)
async def run_classify_email_domain_agent(
    input: ClassifyEmailDomainAgentInput,
) -> ClassifyEmailDomainAgentOutput:
    """You are an email domain classification expert.

    Analyze the provided email domain and classify it into one of three categories:

    - 'invalid_domain': if the domain is not properly formatted or cannot exist (e.g., missing TLD, invalid characters)
    - 'personal_email_domain': if the domain is from a known consumer email provider (e.g., gmail.com, yahoo.com, hotmail.com)
    - 'company_email_domain': if the domain appears to be a legitimate business or organization domain

    Provide your classification in the result field."""
    ...
