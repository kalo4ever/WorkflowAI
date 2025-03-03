import logging
from contextlib import contextmanager
from typing import Any, NoReturn, Protocol

from core.domain.errors import InternalError, MissingEnvVariablesError, ProviderError, StructuredGenerationError
from core.domain.models import Provider
from core.domain.models.model_data import FinalModelData, ModelData
from core.domain.models.utils import get_model_data
from core.providers.base.abstract_provider import AbstractProvider
from core.providers.base.config import ProviderConfig
from core.providers.base.provider_options import ProviderOptions
from core.runners.workflowai.templates import TemplateName
from core.runners.workflowai.workflowai_options import WorkflowAIRunnerOptions


class ProviderPipelineBuilder(Protocol):
    def __call__(
        self,
        model_data: FinalModelData,
        is_structured_generation_enabled: bool,
        provider_type: Provider,
        provider_config: tuple[str, ProviderConfig] | None,
    ) -> tuple[AbstractProvider[Any, Any], TemplateName, ProviderOptions, ModelData]: ...


class ProviderPipeline:
    def __init__(
        self,
        options: WorkflowAIRunnerOptions,
        provider_config: tuple[str, ProviderConfig] | None,
        builder: ProviderPipelineBuilder,
    ):
        self._options = options
        self.model_data = get_model_data(options.model)
        self.provider_config = provider_config
        self.errors: list[ProviderError] = []
        self.builder = builder
        self._force_structured_generation = options.is_structured_generation_enabled
        self._last_error_was_structured_generation = False
        self._logger = logging.getLogger(self.__class__.__name__)

    def raise_on_end(self, task_id: str) -> NoReturn:
        # TODO: metric
        raise (
            self.errors[0]
            if self.errors
            else InternalError(
                "No provider found",
                extras={"task_id": task_id, "options": self._options.model_dump()},
            )
        )

    @contextmanager
    def wrap_provider_call(self, provider: AbstractProvider[Any, Any]):
        try:
            yield
        except StructuredGenerationError as e:
            self._last_error_was_structured_generation = True
            e.capture_if_needed()
            if self._force_structured_generation is None:
                # In this case we will retry without structured generation
                return
            raise e
        except ProviderError as e:
            e.capture_if_needed()
            self.errors.append(e)
            # TODO: add metric and monitor overall provider health
            if provider.config_id is not None:
                # In case of custom configs, we always retry
                return

            if e.should_try_next_provider:
                # Otherwise we retry only if the error should be retried
                return

            raise e

    def _should_retry_without_structured_generation(self):
        # We pop the flag and set the force structured generation to false to
        # trigger a provider without structured gen only
        if self._last_error_was_structured_generation and self._force_structured_generation is None:
            self._force_structured_generation = True
            self._last_error_was_structured_generation = False
            return True

        return False

    def provider_iterator(self):
        def _structured_output():
            if self._force_structured_generation is not None:
                return self._force_structured_generation
            return self.model_data.supports_structured_output

        if self.provider_config:
            yield self.builder(
                self.model_data,
                _structured_output(),
                self.provider_config[1].provider,
                self.provider_config,
            )

        if self._options.provider:
            yield self.builder(
                self.model_data,
                _structured_output(),
                self._options.provider,
                None,
            )
            if self._should_retry_without_structured_generation():
                yield self.builder(
                    self.model_data,
                    False,
                    self._options.provider,
                    None,
                )
            return

        for provider, provider_data in self.model_data.providers:
            # We only use the override for the default pipeline
            provider_model_data = provider_data.override(self.model_data)

            # We only need to wrap the first call in a try/except block
            # Since the env var are present once they will be present always.
            try:
                yield self.builder(
                    provider_model_data,
                    _structured_output(),
                    provider,
                    None,
                )
            except MissingEnvVariablesError as e:
                self._logger.exception(e, extra={"provider": provider})
                continue

            if self._should_retry_without_structured_generation():
                yield self.builder(
                    self.model_data,
                    False,
                    provider,
                    None,
                )
