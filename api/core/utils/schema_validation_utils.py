import logging
from typing import Annotated, Any

_logger = logging.getLogger(__name__)


def fix_non_object_root(
    schema: dict[str, Any],
) -> tuple[
    Annotated[dict[str, Any], "the fixed (optionally) schema"],
    Annotated[bool, "wether the schema was fixed or not"],
]:
    """
    Fixes the cases when the schema is not a clean "type": "object" schema.
    But rather a "type": "array" or a simple type (string, number, boolean, etc.)
    """
    # If schema has no type, and no properties, wrap the schema in a generic "object" type
    if "type" not in schema and "properties" not in schema:
        fixed_schema = {"type": "object", "properties": schema.copy()}
        _logger.error(
            "Fixed schema with no type and no properties at root",
            extra={"schema": schema},
        )
        return fixed_schema, True

    if schema.get("type") and schema.get("type") != "object":
        if schema.get("type") == "array":
            # A generic "items" property is added to the schema
            _logger.error(
                "Fixed schema with type array at root",
                extra={"schema": schema},
            )
            return {"type": "object", "properties": {"items": schema.copy()}, "required": ["items"]}, True

        # All others cases (string, number, boolean, etc.)
        # A generic "output" property is added to the schema
        _logger.error(
            "Fixed schema",
            extra={"schema": schema, "schema_type": schema.get("type")},
        )
        return {"type": "object", "properties": {"output": schema.copy()}, "required": ["output"]}, True

    return schema, False
