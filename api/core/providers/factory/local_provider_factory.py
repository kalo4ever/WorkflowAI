import datetime
import logging
from typing import Any, Iterator

from typing_extensions import override

from core.domain.errors import (
    MissingEnvVariablesError,
    NoProviderSupportingModelError,
)
from core.domain.models import Model, Provider
from core.domain.models.utils import get_model_data, is_model_available_at_provider
from core.domain.organization_settings import ProviderConfig
from core.providers.amazon_bedrock.amazon_bedrock_provider import AmazonBedrockProvider
from core.providers.anthropic.anthropic_provider import AnthropicProvider
from core.providers.base.abstract_provider import AbstractProvider, ProviderConfigVar
from core.providers.factory.abstract_provider_factory import AbstractProviderFactory
from core.providers.fireworks.fireworks_provider import FireworksAIProvider
from core.providers.google.gemini.gemini_api_provider import GoogleGeminiAPIProvider
from core.providers.google.google_provider import GoogleProvider
from core.providers.groq.groq_provider import GroqProvider
from core.providers.mistral.mistral_provider import MistralAIProvider
from core.providers.openai.azure_open_ai_provider.azure_openai_provider import AzureOpenAIProvider
from core.providers.openai.openai_provider import OpenAIProvider

_provider_cls: list[type[AbstractProvider[Any, Any]]] = [
    OpenAIProvider,
    AzureOpenAIProvider,
    GroqProvider,
    GoogleProvider,
    AmazonBedrockProvider,
    MistralAIProvider,
    AnthropicProvider,
    GoogleGeminiAPIProvider,
    FireworksAIProvider,
]


class LocalProviderFactory(AbstractProviderFactory):
    """A provider factory that uses locally defined providers.
    To add a supported provider, add it to the PROVIDER_TYPES list."""

    PROVIDER_TYPES: dict[Provider, type[AbstractProvider[Any, Any]]] = {
        provider.name(): provider for provider in _provider_cls
    }

    def __init__(self) -> None:
        self._providers: dict[Provider, AbstractProvider[Any, Any]] = {}
        self._logger = logging.getLogger(self.__class__.__name__)

    @override
    def get_provider(self, provider: Provider, index: int = 0) -> AbstractProvider[Any, Any]:
        if provider not in self._providers:
            try:
                provider_type = self.PROVIDER_TYPES[provider]
            except KeyError:
                raise ValueError(f"Provider {provider} not supported")
            self._providers[provider] = provider_type.from_env()
        return self._providers[provider]

    def prepare_all_providers(self):
        for provider_name in LocalProviderFactory.PROVIDER_TYPES.keys():
            try:
                provider = self.get_provider(provider_name)
                self._logger.info(
                    "Successfully prepared provider",
                    extra={"provider_name": provider_name, "config": provider.config},
                )
            except MissingEnvVariablesError:
                self._logger.warning(
                    "Skipping provider",
                    extra={"provider_name": provider_name},
                    exc_info=True,
                )
            except Exception:
                self._logger.exception("Failed to prepare provider", extra={"provider_name": provider_name})

        provider_names = ", ".join(list(self._providers.keys()))
        self._logger.info(f"Prepared providers {provider_names}")  # noqa: G004

    # TODO: this is deprecated, use provider pipeline instead
    @override
    def providers_supporting_model(
        self,
        model: Model,
        only_configured: bool = True,
    ) -> Iterator[AbstractProvider[Any, Any]]:
        """Iterate over providers that support the given model.
        Optionally filter out providers that are not configured."""
        today = datetime.date.today()

        providers = get_model_data(model).providers

        # Use 'set' to avoid provider that appear twice in the list (ex: AmazonBedrockProvider)
        for provider, _ in providers:
            provider_type = self.get_provider(provider)
            if (not only_configured or provider_type.is_configured()) and provider_type.supports_model(model):
                model_available = is_model_available_at_provider(provider_type.name(), model, today)
                if model_available:
                    yield provider_type

    @override
    def provider_types_supporting_model(self, model: Model) -> Iterator[type[AbstractProvider[Any, Any]]]:
        """Iterate over providers that support the given model.
        Optionally filter out providers that are not configured."""

        for provider_type in self.PROVIDER_TYPES.values():
            try:
                if provider_type().supports_model(model):
                    yield provider_type
            except MissingEnvVariablesError:  # Catch cases where the provider is not configured
                pass

    @override
    def provider_type(self, config: ProviderConfigVar) -> type[AbstractProvider[ProviderConfigVar, Any]]:
        """Return the provider type for the given provider."""
        return self.PROVIDER_TYPES[config.provider]

    @override
    def build_provider(self, config: ProviderConfig, config_id: str) -> AbstractProvider[Any, Any]:
        """Build a provider from a configuration dictionary."""
        return self.provider_type(config)(config=config, config_id=config_id)

    @override
    def list_provider_x_models(self) -> Iterator[tuple[AbstractProvider[Any, Any], Model]]:
        """Returns all available provider-model pairs."""

        for model in Model:
            for provider in self.providers_supporting_model(model):
                yield provider, model

    def preferred_provider(self, model: Model) -> AbstractProvider[Any, Any]:
        try:
            return next(self.providers_supporting_model(model))
        except StopIteration:
            raise NoProviderSupportingModelError(
                model=model,
                available_providers=list(self._providers.keys()),
            )


_shared_provider_factory = LocalProviderFactory()


def shared_provider_factory() -> LocalProviderFactory:
    return _shared_provider_factory
