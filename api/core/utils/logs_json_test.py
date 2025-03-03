import logging
from io import StringIO

import pytest

from core.utils.logs_json import CappedJsonFormatter


class TestCappedJsonFormatter:
    @pytest.fixture
    def log_stream(self):
        return StringIO()

    @pytest.fixture
    def logger(self, log_stream: StringIO):
        logger = logging.getLogger(__name__)
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(CappedJsonFormatter(max_length=50))
        for h in logger.handlers:
            logger.removeHandler(h)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def test_no_extra(self, logger: logging.Logger, log_stream: StringIO):
        logger.info("Hello, world!")
        assert log_stream.getvalue() == '{"message": "Hello, world!"}\n'

    def test_extra(self, logger: logging.Logger, log_stream: StringIO):
        logger.info("Hello, world!", extra={"bla": "test"})
        assert log_stream.getvalue() == '{"message": "Hello, world!", "bla": "test"}\n'

    def test_too_long(self, logger: logging.Logger, log_stream: StringIO):
        logger.info("Hello, world!" * 100)
        assert log_stream.getvalue() == '{"message": "Hello, world!Hello, world!Hello, worl\n'
