from abc import ABC, abstractmethod
from typing import Any, Iterator

from core.domain.models import Model, Provider
from core.providers.base.abstract_provider import AbstractProvider, ProviderConfigVar
from core.providers.base.config import ProviderConfig


class AbstractProviderFactory(ABC):
    @abstractmethod
    def build_provider(self, config: ProviderConfig, config_id: str) -> AbstractProvider[Any, Any]:
        pass

    @abstractmethod
    def get_provider(self, provider: Provider) -> AbstractProvider[Any, Any]:
        pass

    @abstractmethod
    def providers_supporting_model(self, model: Model) -> Iterator[AbstractProvider[Any, Any]]:
        """Iterate over providers that support the given model."""
        return
        yield

    @abstractmethod
    def provider_types_supporting_model(self, model: Model) -> Iterator[type[AbstractProvider[Any, Any]]]:
        """Iterate over provider types that support the given model."""
        return
        yield

    @abstractmethod
    def list_provider_x_models(self) -> Iterator[tuple[AbstractProvider[Any, Any], Model]]:
        """Returns all available provider-model pairs."""

        return
        yield

    @abstractmethod
    def provider_type(self, config: ProviderConfigVar) -> type[AbstractProvider[ProviderConfigVar, Any]]:
        pass
