from typing import Any

from core.providers.base.abstract_provider import AbstractProvider
from core.providers.factory.local_provider_factory import LocalProviderFactory
from core.providers.openai.azure_open_ai_provider.azure_openai_provider import AzureOpenAIProvider


def list_provider_models_exhaustive_test() -> None:
    provider_models = LocalProviderFactory().list_provider_x_models()

    # Extract a set of all providers in the provider_models
    provider_set: set[type[AbstractProvider[Any, Any]]] = set()
    for provider, _ in provider_models:
        provider_set.add(type(provider))

    expected_provider_set = set(LocalProviderFactory().PROVIDER_TYPES.values())

    # TODO: Remove .add(...) this when some AzureOpenAI models will actually be activated.
    provider_set.add(AzureOpenAIProvider)

    assert provider_set == expected_provider_set
