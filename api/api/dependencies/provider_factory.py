from typing import Annotated

from fastapi import Depends

from api.services.providers_service import shared_provider_factory
from core.providers.factory.abstract_provider_factory import AbstractProviderFactory


def _provider_factory() -> AbstractProviderFactory:
    return shared_provider_factory()


ProviderFactoryDep = Annotated[AbstractProviderFactory, Depends(_provider_factory)]
