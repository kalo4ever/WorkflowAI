import pytest

from core.domain.search_query import SearchOperationSingle, SearchOperator
from core.storage.clickhouse.models.utils import (
    clickhouse_query,
    validate_fixed,
)


class TestValidateFixed:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("10", "10"),
            ("100001", "10000"),
            ("abcde", "abcde"),
            # Last character is stripped entirely since it makes the string too long
            # when encoded
            ("abcdéa", "abcd"),
        ],
    )
    def test_not_raise(self, value: str, expected: str):
        assert validate_fixed(size=5, log_name="bla").func(value) == expected  # type: ignore


class TestClickhouseQuery:
    def test_is_empty(self):
        query = clickhouse_query("key", SearchOperationSingle(SearchOperator.IS_EMPTY, None), "String")
        raw = query.to_sql()
        assert raw
        assert raw[0] == "empty(key)"
        assert not raw[1]

    def test_is_empty_no_type(self):
        query = clickhouse_query("key", SearchOperationSingle(SearchOperator.IS_EMPTY, None))
        raw = query.to_sql()
        assert raw
        assert raw[0] == "isNull(key)"
        assert not raw[1]

    def test_contains(self):
        query = clickhouse_query("key", SearchOperationSingle(SearchOperator.CONTAINS, "test"), "String")
        raw = query.to_sql()
        assert raw
        assert raw[0] == "key ILIKE {v0:String}"
        assert raw[1] == {"v0": "%test%"}
