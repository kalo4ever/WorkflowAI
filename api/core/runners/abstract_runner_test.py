from typing import Any
from unittest.mock import Mock, patch

import pytest

from core.domain.errors import JSONSchemaValidationError, MissingCacheError
from core.domain.run_output import RunOutput
from core.domain.task_group_properties import TaskGroupProperties
from core.domain.task_run_builder import TaskRunBuilder
from core.domain.task_variant import SerializableTaskVariant
from core.domain.types import CacheUsage
from core.runners.builder_context import builder_context
from core.tools import ToolKind
from tests.dummy_runner import DummyRunner
from tests.models import task_run_ser


async def assert_builder_not_empty(*args: Any, **kwargs: Any) -> RunOutput:
    assert builder_context.get() is not None
    return RunOutput({"say_hello": "bla"})


@pytest.fixture
def dummy_runner(hello_task: SerializableTaskVariant, mock_cache_fetcher: Mock) -> DummyRunner:
    builder_context.set(None)
    return DummyRunner(task=hello_task, cache_fetcher=mock_cache_fetcher)


async def test_builder_context_run_present(dummy_runner: DummyRunner, hello_task: SerializableTaskVariant) -> None:
    assert builder_context.get() is None, "sanity check"

    with patch.object(dummy_runner, "_build_task_output") as mock:
        mock.side_effect = assert_builder_not_empty

        res = await dummy_runner.run(
            TaskRunBuilder(task=hello_task, task_input={}, properties=TaskGroupProperties(), start_time=0),
        )
        assert res.task_output == {"say_hello": "bla"}

    mock.assert_called_once()


async def test_builder_context_stream_present(dummy_runner: DummyRunner, hello_task: SerializableTaskVariant) -> None:
    builder_context.set(None)

    assert builder_context.get() is None

    builder = TaskRunBuilder(task=hello_task, task_input={}, properties=TaskGroupProperties(), start_time=0)

    with patch.object(dummy_runner, "_build_task_output") as mock:
        mock.side_effect = assert_builder_not_empty

        async for res in dummy_runner.stream(builder):
            pass

        assert res == RunOutput({"say_hello": "bla"})  # type: ignore

    mock.assert_called_once()


@pytest.fixture(scope="function")
def patched_logger():
    # current = abstract_runner._logger  # pyright: ignore [reportPrivateUsage]
    mock_logger = Mock()

    with patch("core.runners.abstract_runner._logger", new=mock_logger):
        yield mock_logger

    # abstract_runner._logger = current  # pyright: ignore [reportPrivateUsage]


class TestFromCache:
    async def test_from_cache(
        self,
        mock_cache_fetcher: Mock,
        patched_logger: Mock,
        dummy_runner: DummyRunner,
        hello_task: SerializableTaskVariant,
    ):
        run = task_run_ser(task=hello_task)
        mock_cache_fetcher.return_value = run

        res = await dummy_runner.from_cache({})
        assert res == run

        patched_logger.exception.assert_not_called()


class TestCacheOrNone:
    async def test_cache_or_none_auto_temperature_none(
        self,
        mock_cache_fetcher: Mock,
        patched_logger: Mock,
        dummy_runner: DummyRunner,
        hello_task: SerializableTaskVariant,
    ):
        run = task_run_ser(task=hello_task)
        mock_cache_fetcher.return_value = run
        res = await dummy_runner._cache_or_none({}, "auto")  # pyright: ignore [reportPrivateUsage]
        assert res is None

    async def test_cache_or_none_auto_temperature_zero(
        self,
        mock_cache_fetcher: Mock,
        patched_logger: Mock,
        dummy_runner: DummyRunner,
        hello_task: SerializableTaskVariant,
    ):
        run = task_run_ser(task=hello_task)
        mock_cache_fetcher.return_value = run
        dummy_runner.properties.temperature = 0
        res = await dummy_runner._cache_or_none({}, "auto")  # pyright: ignore [reportPrivateUsage]
        assert res == run

    async def test_cache_or_none_auto_temperature_not_zero(
        self,
        mock_cache_fetcher: Mock,
        patched_logger: Mock,
        dummy_runner: DummyRunner,
        hello_task: SerializableTaskVariant,
    ):
        run = task_run_ser(task=hello_task)
        mock_cache_fetcher.return_value = run
        dummy_runner.properties.temperature = 0.1
        res = await dummy_runner._cache_or_none({}, "auto")  # pyright: ignore [reportPrivateUsage]
        assert res is None

    async def test_cache_or_none_always(
        self,
        mock_cache_fetcher: Mock,
        patched_logger: Mock,
        dummy_runner: DummyRunner,
        hello_task: SerializableTaskVariant,
    ):
        run = task_run_ser(task=hello_task)
        mock_cache_fetcher.return_value = run
        res = await dummy_runner._cache_or_none({}, "always")  # pyright: ignore [reportPrivateUsage]
        assert res == run

    async def test_cache_or_none_always_when_available_no_cache(
        self,
        mock_cache_fetcher: Mock,
        patched_logger: Mock,
        dummy_runner: DummyRunner,
        hello_task: SerializableTaskVariant,
    ):
        mock_cache_fetcher.return_value = None
        res = await dummy_runner._cache_or_none({}, "when_available")  # pyright: ignore [reportPrivateUsage]
        assert res is None

    async def test_cache_or_none_always_when_available(
        self,
        mock_cache_fetcher: Mock,
        patched_logger: Mock,
        dummy_runner: DummyRunner,
        hello_task: SerializableTaskVariant,
    ):
        run = task_run_ser(task=hello_task)
        mock_cache_fetcher.return_value = run
        res = await dummy_runner._cache_or_none({}, "when_available")  # pyright: ignore [reportPrivateUsage]
        assert res == run

    async def test_cache_or_none_always_no_cache(
        self,
        mock_cache_fetcher: Mock,
        patched_logger: Mock,
        dummy_runner: DummyRunner,
    ):
        mock_cache_fetcher.return_value = None
        res = await dummy_runner._cache_or_none({}, "always")  # pyright: ignore [reportPrivateUsage]
        assert res is None  # always should not raise, as it replaces "when_available"

    async def test_cache_or_none_only(
        self,
        mock_cache_fetcher: Mock,
        patched_logger: Mock,
        dummy_runner: DummyRunner,
        hello_task: SerializableTaskVariant,
    ):
        run = task_run_ser(task=hello_task)
        mock_cache_fetcher.return_value = run
        res = await dummy_runner._cache_or_none({}, "only")  # pyright: ignore [reportPrivateUsage]
        assert res == run

    async def test_cache_or_none_only_not_found(
        self,
        mock_cache_fetcher: Mock,
        patched_logger: Mock,
        dummy_runner: DummyRunner,
        hello_task: SerializableTaskVariant,
    ):
        mock_cache_fetcher.return_value = None
        with pytest.raises(MissingCacheError):
            await dummy_runner._cache_or_none({}, "only")  # pyright: ignore [reportPrivateUsage]

    async def test_cache_or_none_never(self, mock_cache_fetcher: Mock, patched_logger: Mock, dummy_runner: DummyRunner):
        run = task_run_ser(task=dummy_runner.task)
        mock_cache_fetcher.return_value = run
        res = await dummy_runner._cache_or_none({}, "never")  # pyright: ignore [reportPrivateUsage]
        assert res is None

    async def test_from_cache(self, mock_cache_fetcher: Mock, dummy_runner: DummyRunner):
        run = task_run_ser(task=dummy_runner.task, from_cache=False)
        assert not run.from_cache
        mock_cache_fetcher.return_value = run
        res = await dummy_runner.from_cache({})
        assert res
        assert res.from_cache


class TestShouldUseCache:
    @pytest.mark.parametrize(
        ("cache", "expected"),
        [("never", False), ("always", True), ("only", True), ("when_available", True), ("auto", True)],
    )
    async def test_with_temperature_zero(self, dummy_runner: DummyRunner, cache: CacheUsage, expected: bool):
        dummy_runner.properties.temperature = 0
        assert dummy_runner._should_use_cache(cache) == expected  # pyright: ignore [reportPrivateUsage]

    @pytest.mark.parametrize(
        ("cache", "expected"),
        [("never", False), ("always", True), ("only", True), ("when_available", True), ("auto", False)],
    )
    async def test_with_temperature_one(self, dummy_runner: DummyRunner, cache: CacheUsage, expected: bool):
        dummy_runner.properties.temperature = 1
        assert dummy_runner._should_use_cache(cache) == expected  # pyright: ignore [reportPrivateUsage]

    @pytest.mark.parametrize(
        ("cache", "expected"),
        [("never", False), ("always", True), ("only", True), ("when_available", True), ("auto", False)],
    )
    async def test_with_tools(self, dummy_runner: DummyRunner, cache: CacheUsage, expected: bool):
        dummy_runner.properties.temperature = 0
        dummy_runner.properties.enabled_tools = [ToolKind.WEB_BROWSER_TEXT]
        assert dummy_runner._should_use_cache(cache) == expected  # pyright: ignore [reportPrivateUsage]


class TestTaskRunBuilder:
    async def test_task_run_builder_on_invalid_schema(self, dummy_runner: DummyRunner):
        task_input = {"name": 1}

        with pytest.raises(JSONSchemaValidationError):
            dummy_runner.task.validate_input(task_input)

        builder = await dummy_runner.task_run_builder(input=task_input, start_time=0)
        assert builder.task_input == task_input
