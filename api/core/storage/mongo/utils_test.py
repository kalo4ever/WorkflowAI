from collections.abc import Callable
from typing import Any, Awaitable

import pytest

from core.domain.search_query import SearchOperator
from core.storage.mongo.mongo_types import AsyncCollection

from .utils import (
    add_filter,
    array_length_filter,
    extract_connection_info,
    is_empty_filter,
    is_not_empty_filter,
    projection,
)


@pytest.mark.parametrize(
    "conn, exp_url, exp_name",
    [
        (
            "mongodb://localhost:27017/mydb?retryWrites=true&w=majority",
            "mongodb://localhost:27017/?retryWrites=true&w=majority",
            "mydb",
        ),
        (
            "mongodb://localhost:27017/mydb",
            "mongodb://localhost:27017/",
            "mydb",
        ),
        (
            # Db name is included elsewhere in the connection string
            "mongodb://localhost:27017/localhost?retryWrites=true&w=majority",
            "mongodb://localhost:27017/?retryWrites=true&w=majority",
            "localhost",
        ),
    ],
)
def test_extract_database_name(conn: str, exp_url: str, exp_name: str) -> None:
    url, name, _ = extract_connection_info(conn)
    assert url == exp_url
    assert name == exp_name


@pytest.mark.parametrize(
    "url, exp_ca_file",
    [
        ("mongodb://localhost:27017/mydb?retryWrites=true&w=majority", False),
        ("mongodb://localhost:27017/mydb?ssl=true", True),
        ("mongodb://localhost:27017/mydb?ssl=false", False),
        ("mongodb://localhost:27017/mydb", False),
        ("mongodb+srv://localhost:27017/mydb?ssl=true", True),
        ("mongodb+srv://localhost:27017/mydb?ssl=false", False),
        ("mongodb+srv://localhost:27017/mydb", True),
        ("mongodb://localhost:27017/mydb?tls=true", True),
        ("mongodb://localhost:27017/mydb?tlsCAFile=/hello/app.pem", "/hello/app.pem"),
    ],
)
def test_ca_file(url: str, exp_ca_file: bool | str) -> None:
    _, _, ca_file = extract_connection_info(url)
    if not exp_ca_file:
        assert ca_file is None
    elif exp_ca_file is True:
        assert ca_file is not None and ca_file != ""
    else:
        assert ca_file == exp_ca_file


class TestProjection:
    def test_without_mapping(self) -> None:
        assert projection(include=["a", "b"], exclude=["c"]) == {"a": 1, "b": 1, "c": 0}

    def test_with_no_include_or_exclude(self) -> None:
        assert projection() is None

    def test_with_mapping(self) -> None:
        assert projection(include=["a", "b"], exclude=["c"], mapping={"a": "A", "b": "B"}) == {
            "A": 1,
            "B": 1,
            "c": 0,
        }


class TestAddFilter:
    def test_new_key(self) -> None:
        current: dict[str, Any] = {}
        add_filter(current, "field", "value")
        assert current == {"field": "value"}

    def test_and_merge(self) -> None:
        current: dict[str, Any] = {"$and": [{"a": 1}]}
        add_filter(current, "$and", [{"b": 2}])
        assert current == {"$and": [{"a": 1}, {"b": 2}]}

    def test_or_merge(self) -> None:
        current: dict[str, Any] = {"$or": [{"a": 1}]}
        add_filter(current, "$or", [{"b": 2}])
        assert current == {"$and": [{"$or": [{"a": 1}]}, {"$or": [{"b": 2}]}]}

    def test_expr_merge(self) -> None:
        current: dict[str, Any] = {"$expr": {"$eq": ["$field1", 1]}}
        add_filter(current, "$expr", {"$eq": ["$field2", 2]})
        assert current == {"$expr": {"$and": [{"$eq": ["$field1", 1]}, {"$eq": ["$field2", 2]}]}}

    def test_operator_merge(self) -> None:
        current: dict[str, Any] = {"field": {"$gte": 5}}
        add_filter(current, "field", {"$lte": 10})
        assert current == {"field": {"$gte": 5, "$lte": 10}}

    def test_invalid_and_value(self) -> None:
        current: dict[str, Any] = {"$and": [{"a": 1}]}
        with pytest.raises(ValueError, match="Expected a list for \\$and"):
            add_filter(current, "$and", {"b": 2})

    def test_invalid_or_value(self) -> None:
        current: dict[str, Any] = {"$or": [{"a": 1}]}
        with pytest.raises(ValueError, match="Expected a list for \\$or"):
            add_filter(current, "$or", {"b": 2})

    def test_cannot_merge_scalar_values(self) -> None:
        current: dict[str, Any] = {"field": "value1"}
        add_filter(current, "field", "value2")
        # The current value is lost and warning is logged
        assert current == {"field": "value2"}


async def _insert_values(collection: AsyncCollection, *args: Any):
    """Inserts values with a deterministic id and returns a function to fetch the ids given a filter"""
    await collection.delete_many({})
    await collection.insert_many(
        [
            {
                "_id": f"{i}",
                "value": value,
            }
            for i, value in enumerate(args)
        ],
    )
    # Also insert one where the value is missing
    await collection.insert_one({"_id": f"{len(args)}"})

    async def fetch_ids(filter: dict[str, Any]) -> list[str]:
        return sorted([doc["_id"] async for doc in collection.find(filter)])

    return fetch_ids


class TestEmptyFilters:
    async def test_is_empty_string(self, collection: AsyncCollection):
        fetch_ids = await _insert_values(collection, "", "not empty", None)

        assert await fetch_ids(is_empty_filter("string", "value")) == ["0", "2", "3"]
        assert await fetch_ids(is_not_empty_filter("string", "value")) == ["1"]

    async def test_is_empty_number(self, collection: AsyncCollection):
        fetch_ids = await _insert_values(collection, 0, 1, None)

        assert await fetch_ids(is_empty_filter("number", "value")) == ["0", "2", "3"]
        assert await fetch_ids(is_not_empty_filter("number", "value")) == ["1"]

    async def test_is_empty_array(self, collection: AsyncCollection):
        fetch_ids = await _insert_values(collection, [], [1], None)

        assert await fetch_ids(is_empty_filter("array", "value")) == ["0", "2", "3"]
        assert await fetch_ids(is_not_empty_filter("array", "value")) == ["1"]

    async def test_is_empty_bool(self, collection: AsyncCollection):
        fetch_ids = await _insert_values(collection, True, False, None)

        assert await fetch_ids(is_empty_filter("boolean", "value")) == ["2", "3"]
        assert await fetch_ids(is_not_empty_filter("boolean", "value")) == ["0", "1"]


# TODO: likely no longer needed
class TestArrayLengthFilter:
    @pytest.fixture
    async def fetcher(self, collection: AsyncCollection):
        # Insert test data with arrays of different lengths
        return await _insert_values(
            collection,
            [],  # Empty array
            [1],  # Length 1
            [1, 2],  # Length 2
            [1, 2, 3],  # Length 3
            None,  # null value
        )

    async def test_is(self, fetcher: Callable[[dict[str, Any]], Awaitable[list[str]]]) -> None:
        # Test IS operator
        assert await fetcher(array_length_filter(SearchOperator.IS, "value", 0)) == ["0", "4", "5"]
        assert await fetcher(array_length_filter(SearchOperator.IS, "value", 1)) == ["1"]
        assert await fetcher(array_length_filter(SearchOperator.IS, "value", 2)) == ["2"]
        assert await fetcher(array_length_filter(SearchOperator.IS, "value", 3)) == ["3"]

    async def test_is_not(self, fetcher: Callable[[dict[str, Any]], Awaitable[list[str]]]) -> None:
        assert await fetcher(array_length_filter(SearchOperator.IS_NOT, "value", 0)) == ["1", "2", "3"]
        assert await fetcher(array_length_filter(SearchOperator.IS_NOT, "value", 1)) == ["0", "2", "3", "4", "5"]

    async def test_greater_than(self, fetcher: Callable[[dict[str, Any]], Awaitable[list[str]]]) -> None:
        assert await fetcher(array_length_filter(SearchOperator.GREATER_THAN, "value", 0)) == ["1", "2", "3"]
        assert await fetcher(array_length_filter(SearchOperator.GREATER_THAN, "value", 1)) == ["2", "3"]
        assert await fetcher(array_length_filter(SearchOperator.GREATER_THAN, "value", 2)) == ["3"]
        assert await fetcher(array_length_filter(SearchOperator.GREATER_THAN, "value", 3)) == []

    async def test_greater_than_or_equal_to(self, fetcher: Callable[[dict[str, Any]], Awaitable[list[str]]]) -> None:
        assert await fetcher(array_length_filter(SearchOperator.GREATER_THAN_OR_EQUAL_TO, "value", 0)) == [
            "0",
            "1",
            "2",
            "3",
            "4",
        ]
        assert await fetcher(array_length_filter(SearchOperator.GREATER_THAN_OR_EQUAL_TO, "value", 1)) == [
            "1",
            "2",
            "3",
        ]
        assert await fetcher(array_length_filter(SearchOperator.GREATER_THAN_OR_EQUAL_TO, "value", 2)) == [
            "2",
            "3",
        ]

    async def test_less_than(self, fetcher: Callable[[dict[str, Any]], Awaitable[list[str]]]) -> None:
        assert await fetcher(array_length_filter(SearchOperator.LESS_THAN, "value", 1)) == ["0", "4", "5"]
        assert await fetcher(array_length_filter(SearchOperator.LESS_THAN, "value", 2)) == ["0", "1", "4", "5"]
        assert await fetcher(array_length_filter(SearchOperator.LESS_THAN, "value", 3)) == [
            "0",
            "1",
            "2",
            "4",
            "5",
        ]

    async def test_less_than_or_equal_to(self, fetcher: Callable[[dict[str, Any]], Awaitable[list[str]]]) -> None:
        assert await fetcher(array_length_filter(SearchOperator.LESS_THAN_OR_EQUAL_TO, "value", 0)) == [
            "0",
            "4",
            "5",
        ]
        assert await fetcher(array_length_filter(SearchOperator.LESS_THAN_OR_EQUAL_TO, "value", 1)) == [
            "0",
            "1",
            "4",
            "5",
        ]
        assert await fetcher(array_length_filter(SearchOperator.LESS_THAN_OR_EQUAL_TO, "value", 2)) == [
            "0",
            "1",
            "2",
            "4",
            "5",
        ]
