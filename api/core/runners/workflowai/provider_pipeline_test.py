from unittest.mock import Mock

import pytest

from core.domain.errors import MissingEnvVariablesError
from core.domain.models import Model, Provider
from core.domain.models.model_data import FinalModelData
from core.providers.base.config import ProviderConfig
from core.runners.workflowai.provider_pipeline import ProviderPipeline, ProviderPipelineBuilder
from core.runners.workflowai.workflowai_options import WorkflowAIRunnerOptions


@pytest.fixture
def provider_builder():
    builder = Mock(spec=ProviderPipelineBuilder)
    # Last argument is the model data
    builder.side_effect = lambda *args: (Mock(), Mock(), Mock(), args[0])  # type: ignore
    return builder


# TODO: The tests are based on the real model data, we should patch
class TestProviderIterator:
    def test_claude_ordering_and_support(self, provider_builder: Mock):
        pipeline = ProviderPipeline(
            options=WorkflowAIRunnerOptions(
                model=Model.CLAUDE_3_5_SONNET_20241022,
                provider=None,
                is_structured_generation_enabled=None,
                instructions="",
            ),
            provider_config=None,
            builder=provider_builder,
        )

        # List all providers
        providers = list(pipeline.provider_iterator())
        assert len(providers) == 2

        assert provider_builder.call_count == 2

        provider_1 = provider_builder.call_args_list[0].args[2]
        assert provider_1 == Provider.AMAZON_BEDROCK
        # Testing the override
        assert not providers[0][-1].supports_input_pdf

        provider_2 = provider_builder.call_args_list[1].args[2]
        assert provider_2 == Provider.ANTHROPIC
        assert providers[1][-1].supports_input_pdf

    def test_missing_env_vars(self, provider_builder: Mock):
        # GPT is available on azure and openai
        pipeline = ProviderPipeline(
            options=WorkflowAIRunnerOptions(
                model=Model.GPT_4O_2024_11_20,
                provider=None,
                is_structured_generation_enabled=None,
                instructions="",
            ),
            provider_config=None,
            builder=provider_builder,
        )

        def _builder(
            model_data: FinalModelData,
            is_structured_generation_enabled: bool,
            provider_type: Provider,
            provider_config: tuple[str, ProviderConfig] | None,
        ):
            if provider_type == Provider.AZURE_OPEN_AI:
                raise MissingEnvVariablesError(names=["AZURE_OPENAI_API_KEY"])
            return (Mock(), Mock(), Mock(), model_data)

        pipeline.builder = _builder

        # We shoudl just skip the azure provider
        providers = list(pipeline.provider_iterator())
        assert len(providers) == 1
