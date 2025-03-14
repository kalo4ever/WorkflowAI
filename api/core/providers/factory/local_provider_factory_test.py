from collections.abc import Callable
from typing import Any
from unittest.mock import patch

import pytest

from core.domain.models import Model, Provider
from core.providers.groq.groq_provider import GroqProvider
from core.providers.openai.openai_provider import OpenAIProvider

from ..base.abstract_provider import AbstractProvider as AbstractProvider
from .local_provider_factory import LocalProviderFactory


@pytest.fixture
def mock_openai_provider():
    with (
        patch.object(OpenAIProvider, "is_configured", return_value=True),
        patch.object(OpenAIProvider, "supports_model", return_value=True),
    ):
        yield


@pytest.fixture
def mock_groq_provider_supports():
    with (
        patch.object(GroqProvider, "is_configured", return_value=True),
        patch.object(GroqProvider, "supports_model", return_value=True),
    ):
        yield


@pytest.fixture
def mock_groq_provider_does_not_support():
    with (
        patch.object(GroqProvider, "is_configured", return_value=True),
        patch.object(GroqProvider, "supports_model", return_value=False),
    ):
        yield


@pytest.fixture
def mock_model_availability():
    with patch(
        "core.providers.factory.local_provider_factory.is_model_available_at_provider",
        return_value=True,
    ):
        yield


@pytest.fixture
def local_provider_factory():
    return LocalProviderFactory()


def test_providers_supporting_model(
    local_provider_factory: LocalProviderFactory,
    mock_openai_provider: None,
    mock_groq_provider_does_not_support: None,
    mock_model_availability: Callable[[], Any],
):
    supported_providers = list(local_provider_factory.providers_supporting_model(Model.GPT_4O_LATEST))
    assert len(supported_providers) == 2
    names = [provider.name() for provider in supported_providers]
    assert names == [Provider.OPEN_AI, Provider.AZURE_OPEN_AI]


def test_providers_supporting_model_none_configured(local_provider_factory: LocalProviderFactory):
    with patch.object(AbstractProvider, "is_configured", return_value=False):
        supported_providers = list(local_provider_factory.providers_supporting_model(Model.GPT_3_5_TURBO_1106))
        assert len(supported_providers) == 0


def test_providers_supporting_model_not_available(
    local_provider_factory: LocalProviderFactory,
    mock_openai_provider: None,
):
    with patch(
        "core.providers.factory.local_provider_factory.is_model_available_at_provider",
        return_value=False,
    ):
        supported_providers = list(local_provider_factory.providers_supporting_model(Model.GPT_3_5_TURBO_1106))
        assert len(supported_providers) == 0
