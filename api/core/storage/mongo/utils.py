import logging
from collections.abc import Callable, Collection, Iterable
from typing import Any, cast
from urllib.parse import parse_qs, urlparse

import certifi
from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel

from core.domain.search_query import SearchOperator
from core.utils.schemas import FieldType
from core.utils.types import IncEx

_logger = logging.getLogger(__name__)


def dump_model(model: BaseModel, exclude: IncEx = None, include: IncEx = None) -> dict[str, Any]:
    return model.model_dump(by_alias=True, exclude_none=True, exclude=exclude, include=include)  # pyright: ignore[reportArgumentType]


def is_insecure_url(url: str, qs: dict[str, list[str]]) -> bool:
    if "ssl" in qs:
        return qs["ssl"][0] == "false"

    if "tls" in qs:
        return qs["tls"][0] == "false"

    return url.startswith("mongodb://")


def tls_ca_file_from_qs(url: str, qs: dict[str, list[str]]) -> str | None:
    if "tlsCAFile" in qs:
        return qs["tlsCAFile"][0]
    if is_insecure_url(url, qs):
        return None
    return certifi.where()


def extract_connection_info(connection_string: str) -> tuple[str, str, str | None]:
    """Returns a tuple of host, db name, tlsCAFile"""
    o = urlparse(connection_string)
    if not o.path:
        raise ValueError("Could not split db name")

    path = o.path[1:]
    if "/" in path:
        raise ValueError("Could not determine db name")

    return o._replace(path="/").geturl(), path, tls_ca_file_from_qs(connection_string, parse_qs(o.query))


def query_set_filter(q: Collection[Any], inc: bool) -> Any:
    """Returns a filter for matching a set of value or not"""
    if len(q) == 1:
        v = next(iter(q))
        if inc:
            return v
        return {"$ne": v}
    if inc:
        return {"$in": list(q)}
    return {"$nin": list(q)}


def object_id(id: str) -> ObjectId:
    """Wrapper around ObjectId that raises a non mongo specific error"""
    try:
        return ObjectId(id)
    except InvalidId:
        raise AssertionError(f"Invalid ObjectId: {id}")


def projection(
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
    mapping: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    mapper: Callable[[str], str] = (lambda k: mapping.get(k, k)) if mapping else (lambda k: k)

    if not include and not exclude:
        return None
    out: dict[str, Any] = {}
    if include:
        out.update({mapper(k): 1 for k in include})
    if exclude:
        out.update({mapper(k): 0 for k in exclude})
    return out


def add_filter(current: dict[str, Any], key: str, value: Any):
    """Add a filter to an existing mongodb filter. current is modified in place."""
    if key not in current:
        current[key] = value
        return

    match key:
        case "$and":
            if not isinstance(value, list):
                raise ValueError("Expected a list for $and")
            current["$and"].extend(value)
        case "$or":
            if not isinstance(value, list):
                raise ValueError("Expected a list for $or")
            # Preserve existing conditions. New filter becomes
            # and [{$or:...}, {$or:...}]
            add_filter(current, "$and", [{"$or": current.pop("$or")}, {"$or": value}])
        case "$expr":
            add_filter(current, "$expr", {"$and": [current.pop("$expr"), value]})
        case _:
            filter = current.pop(key)
            if isinstance(value, dict):
                # Cases like adding {"$gte": ...}
                if isinstance(filter, dict):
                    current[key] = {**filter, **value}
                    return
            current[key] = value
            _logger.warning(
                "Could not merge filters",
                extra={"current": current, "key": key, "value": cast(Any, value)},
            )


def merge_filters(current: dict[str, Any], new: dict[str, Any]):
    for k, v in new.items():
        add_filter(current, k, v)


def is_empty_filter(type: FieldType | None, key: str) -> dict[str, Any]:
    match type:
        case "string":
            empty_value = ""
        case "array":
            empty_value = []
        case "object":
            empty_value = {}
        case "integer" | "number":
            empty_value = 0
        case "boolean" | "null" | "array_length" | None | "date":
            empty_value = None

    second_check: Any = {"$in": [None, empty_value]} if empty_value is not None else None

    return {
        "$or": [
            {key: {"$exists": False}},
            {key: second_check},
        ],
    }


def is_not_empty_filter(type: FieldType | None, key: str):
    match type:
        case "string":
            return {key: {"$gt": ""}}
        case "number" | "integer":
            return {key: {"$gt": 0}}
        case "array":
            return {f"{key}.0": {"$exists": True}}
        case "boolean":
            return {key: {"$in": [True, False]}}
        case "object" | None | "null" | "array_length" | "date":
            # Unfortunately this means that we are not filter out
            return {key: {"$exists": True}}


def array_length_filter(operator: SearchOperator, key: str, value: int) -> dict[str, Any]:  # noqa C901
    if not value:
        match operator:
            case (
                SearchOperator.IS
                | SearchOperator.LESS_THAN
                | SearchOperator.LESS_THAN_OR_EQUAL_TO
                | SearchOperator.IS_BEFORE
            ):
                return is_empty_filter("array", key)
            case SearchOperator.GREATER_THAN_OR_EQUAL_TO:
                return {key: {"$exists": True}}
            case SearchOperator.GREATER_THAN | SearchOperator.IS_NOT | SearchOperator.IS_AFTER:
                return is_not_empty_filter("array", key)
            case (
                SearchOperator.IS_BETWEEN
                | SearchOperator.IS_NOT_BETWEEN
                | SearchOperator.IS_EMPTY
                | SearchOperator.IS_NOT_EMPTY
                | SearchOperator.CONTAINS
                | SearchOperator.NOT_CONTAINS
            ):
                raise ValueError(f"Unsupported operator for array length: {operator}")
    match operator:
        case SearchOperator.IS:
            return {
                "$and": [
                    {f"{key}.{value - 1}": {"$exists": True}},
                    {f"{key}.{value}": {"$exists": False}},
                ],
            }
        case SearchOperator.GREATER_THAN_OR_EQUAL_TO:
            return {f"{key}.{value - 1}": {"$exists": True}}
        case SearchOperator.IS_NOT:
            return {
                "$or": [
                    {f"{key}.{value - 1}": {"$exists": False}},
                    {f"{key}.{value}": {"$exists": True}},
                ],
            }
        case SearchOperator.GREATER_THAN | SearchOperator.IS_AFTER:
            return {f"{key}.{value}": {"$exists": True}}
        case SearchOperator.LESS_THAN | SearchOperator.IS_BEFORE:
            return {f"{key}.{value - 1}": {"$exists": False}}
        case SearchOperator.LESS_THAN_OR_EQUAL_TO:
            return {f"{key}.{value}": {"$exists": False}}
        case (
            SearchOperator.IS_BETWEEN
            | SearchOperator.IS_NOT_BETWEEN
            | SearchOperator.IS_EMPTY
            | SearchOperator.IS_NOT_EMPTY
            | SearchOperator.CONTAINS
            | SearchOperator.NOT_CONTAINS
        ):
            raise ValueError(f"Unsupported operator for array length: {operator}")
