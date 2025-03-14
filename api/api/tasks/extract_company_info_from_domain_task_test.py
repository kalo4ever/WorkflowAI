from unittest.mock import AsyncMock, patch

from workflowai import WorkflowAIError
from workflowai.core.domain.errors import BaseError

from api.tasks.company_domain_from_email_agent import ClassifyEmailDomainAgentOutput
from api.tasks.extract_company_info_from_domain_task import (
    ExtractCompanyInfoFromDomainTaskOutput,
    Product,
    safe_extract_company_domain,
    safe_generate_company_description_from_email,
)


class TestSafeExtractCompanyDomain:
    async def test_none_email(self):
        result = await safe_extract_company_domain(user_email=None)
        assert result is None

    async def test_invalid_email_domain(self):
        result = await safe_extract_company_domain(user_email="invalid@email")
        assert result is None

    async def test_non_company_domain(self):
        with patch(
            "api.tasks.extract_company_info_from_domain_task.run_classify_email_domain_agent",
            new_callable=AsyncMock,
            return_value=ClassifyEmailDomainAgentOutput(
                result=ClassifyEmailDomainAgentOutput.Result.PERSONAL_EMAIL_DOMAIN,
            ),
        ):
            result = await safe_extract_company_domain(user_email="user@gmail.com")
            assert result is None

    async def test_company_domain_success(self):
        with patch(
            "api.tasks.extract_company_info_from_domain_task.run_classify_email_domain_agent",
            new_callable=AsyncMock,
            return_value=ClassifyEmailDomainAgentOutput(
                result=ClassifyEmailDomainAgentOutput.Result.COMPANY_EMAIL_DOMAIN,
            ),
        ):
            result = await safe_extract_company_domain(user_email="user@company.com")
            assert result == "company.com"

    async def test_workflow_ai_error(self):
        with patch(
            "api.tasks.extract_company_info_from_domain_task.run_classify_email_domain_agent",
            new_callable=AsyncMock,
            side_effect=WorkflowAIError(
                error=BaseError(message="Classification failed"),
                response=None,
            ),
        ):
            result = await safe_extract_company_domain(user_email="user@company.com")
            assert result is None


class TestSafeGenerateCompanyDescription:
    async def test_none_email(self):
        result = await safe_generate_company_description_from_email(user_email=None)
        assert result is None

    async def test_invalid_email_domain(self):
        result = await safe_generate_company_description_from_email(user_email="invalid@email")
        assert result is None

    async def test_non_company_domain(self):
        with patch(
            "api.tasks.extract_company_info_from_domain_task.run_classify_email_domain_agent",
            new_callable=AsyncMock,
            return_value=ClassifyEmailDomainAgentOutput(
                result=ClassifyEmailDomainAgentOutput.Result.PERSONAL_EMAIL_DOMAIN,
            ),
        ):
            result = await safe_generate_company_description_from_email(user_email="user@gmail.com")
            assert result is None

    async def test_company_domain_classification_error(self):
        with patch(
            "api.tasks.extract_company_info_from_domain_task.run_classify_email_domain_agent",
            new_callable=AsyncMock,
            side_effect=WorkflowAIError(
                error=BaseError(message="Extraction failed"),
                response=None,
            ),
        ):
            result = await safe_generate_company_description_from_email(user_email="user@company.com")
            assert result is None

    async def test_extract_company_info_success(self):
        expected_output = ExtractCompanyInfoFromDomainTaskOutput(
            company_name="Test Company",
            description="A test company",
            locations=["Location 1"],
            industries=["Industry 1"],
            products=[Product(name="Product 1", description="A test product")],
        )

        with (
            patch(
                "api.tasks.extract_company_info_from_domain_task.safe_extract_company_domain",
                new_callable=AsyncMock,
                return_value="company.com",
            ),
            patch(
                "api.tasks.extract_company_info_from_domain_task._extract_company_info_from_domain",
                new_callable=AsyncMock,
                return_value=expected_output,
            ),
        ):
            result = await safe_generate_company_description_from_email(user_email="user@company.com")
            assert result == expected_output

    async def test_extract_company_info_error(self):
        with (
            patch(
                "api.tasks.extract_company_info_from_domain_task.run_classify_email_domain_agent",
                new_callable=AsyncMock,
                return_value=ClassifyEmailDomainAgentOutput(
                    result=ClassifyEmailDomainAgentOutput.Result.COMPANY_EMAIL_DOMAIN,
                ),
            ),
            patch(
                "api.tasks.extract_company_info_from_domain_task._extract_company_info_from_domain",
                new_callable=AsyncMock,
                side_effect=WorkflowAIError(
                    error=BaseError(message="Extraction failed"),
                    response=None,
                ),
            ),
        ):
            result = await safe_generate_company_description_from_email(user_email="user@company.com")
            assert result is None
