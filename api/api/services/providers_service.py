from core.providers.factory.local_provider_factory import LocalProviderFactory

_shared_provider_factory = LocalProviderFactory()


def shared_provider_factory() -> LocalProviderFactory:
    return _shared_provider_factory
