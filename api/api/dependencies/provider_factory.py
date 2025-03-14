from typing import Annotated

from fastapi import Depends

from core.providers.factory.abstract_provider_factory import AbstractProviderFactory
from core.providers.factory.local_provider_factory import shared_provider_factory


def _provider_factory() -> AbstractProviderFactory:
    return shared_provider_factory()


ProviderFactoryDep = Annotated[AbstractProviderFactory, Depends(_provider_factory)]
