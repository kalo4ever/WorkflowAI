import asyncio
import logging
import os
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest

from core.storage.mongo.migrations.base import AbstractMigration
from core.storage.mongo.migrations.migrate import MIGRATIONS, MigrationCheckError, check_migrations, migrate
from core.storage.mongo.mongo_storage import MongoStorage


@pytest.fixture(scope="function")
def patched_logger():
    mock_logger = Mock()

    orig_get_logger = logging.getLogger

    def _get_logger(name: str | None = None, *args: Any, **kwargs: Any):
        if name == "core.storage.mongo.migrations.migrate":
            return mock_logger
        return orig_get_logger(name)

    with patch("logging.getLogger", new=_get_logger):
        yield mock_logger


async def test_all_migrations_in_sequence(empty_storage: MongoStorage, patched_logger: Mock):
    # Test that all migrations can be performed in a sequence

    for i in range(0, len(MIGRATIONS)):
        migrations = MIGRATIONS[: i + 1]
        patched_logger.reset_mock()

        await migrate(empty_storage, migrations=migrations, max_retries=0)
        # Logging 5 times + 2 per migration
        assert patched_logger.info.call_count == 7

        msgs = [call[0][0] for call in patched_logger.info.call_args_list]
        assert msgs == [
            "Starting migrations",
            "Acquired migration lock",
            "Performing 1 migrations",
            f"Starting {migrations[-1].name()}",
            f"Finished {migrations[-1].name()}",
            "Finished MIGRATIONS",
            "Releasing migration lock",
        ]


class _DummyMigration(AbstractMigration):
    async def apply(self):
        logging.getLogger("core.storage.mongo.migrations.migrate").info("Applying")

    async def rollback(self):
        assert False


async def test_migration_lock(empty_storage: MongoStorage, patched_logger: Mock):
    # Test that the migration lock is acquired
    patched_logger.reset_mock()

    async def _migrate():
        await migrate(empty_storage, migrations=[_DummyMigration], max_retries=10, sleep_delay=0.1)

    # Creating 2 migrations at the same time
    async with asyncio.TaskGroup() as tg:
        tg.create_task(_migrate())
        tg.create_task(_migrate())

    msgs = [call[0][0] for call in patched_logger.info.call_args_list]
    assert msgs == [
        "Starting migrations",
        "Starting migrations",
        "Acquired migration lock",
        "Performing 1 migrations",
        "Starting _DummyMigration",
        "Applying",
        "Finished _DummyMigration",
        "Finished MIGRATIONS",
        "Releasing migration lock",
        "Acquired migration lock",
        "Performing 0 migrations",
        "Finished MIGRATIONS",
        "Releasing migration lock",
    ]

    patched_logger.reset_mock()

    # trying again for good measure
    await _migrate()
    msgs = [call[0][0] for call in patched_logger.info.call_args_list]
    assert msgs == [
        "Starting migrations",
        "Acquired migration lock",
        "Performing 0 migrations",
        "Finished MIGRATIONS",
        "Releasing migration lock",
    ]


def test_migration_file_count():
    # Count migration files and compare with MIGRATIONS to make sure they match

    migration_dir = os.path.join(os.path.dirname(__file__), "migrations")
    migration_files = [f for f in os.listdir(migration_dir) if f.endswith(".py") and not f.endswith("_test.py")]
    migration_count = len(migration_files)

    assert migration_count == len(MIGRATIONS)


class TestCheckMigrations:
    @pytest.fixture
    def mock_storage(self) -> AsyncMock:  # noqa: F821
        return AsyncMock(spec=MongoStorage)

    async def test_check_migrations_no_migrations(self, mock_storage: Mock):
        mock_storage.list_migrations.return_value = []
        await check_migrations(mock_storage, migrations=[])

    async def test_check_migrations_migrations_in_sync(self, mock_storage: Mock):
        mock_storage.list_migrations.return_value = ["_DummyMigration"]
        await check_migrations(mock_storage, migrations=[_DummyMigration])

    async def test_check_migrations_migrations_not_in_sync(self, mock_storage: Mock):
        mock_storage.list_migrations.return_value = []
        with pytest.raises(MigrationCheckError) as e:
            await check_migrations(mock_storage, migrations=[_DummyMigration])

        assert str(e.value) == "Migrations are needed: ['_DummyMigration']"
