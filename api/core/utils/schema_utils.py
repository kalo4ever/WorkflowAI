from typing import Any

from genson import (  # pyright: ignore[reportMissingTypeStubs]
    SchemaBuilder,  # pyright: ignore[reportUnknownVariableType]
)

from core.utils.schema_sanitation import streamline_schema
from core.utils.schemas import strip_metadata


def json_schema_from_json(data: dict[str, Any]) -> dict[str, Any]:
    """Build a JSON schema from a JSON object."""

    builder: SchemaBuilder = SchemaBuilder()
    builder.add_object(data)  # pyright: ignore[reportUnknownMemberType]
    schema = builder.to_schema()  # pyright: ignore[reportUnknownVariableType]
    schema.pop("$schema", None)  # pyright: ignore[reportUnknownMemberType]
    schema = strip_metadata(schema, keys={"required"})
    return streamline_schema(schema)  # pyright: ignore[reportUnknownArgumentType]
