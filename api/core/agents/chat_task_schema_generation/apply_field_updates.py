from typing import Any, List, cast

from pydantic import BaseModel, Field

from core.utils.schemas import InvalidSchemaError, JsonSchema, RawJsonSchema


class InputFieldUpdate(BaseModel):
    keypath: str = Field(
        description="The keypath of the field to update",
        examples=["team.name", "players.0.name (for arrays)"],
    )
    updated_description: str | None = Field(
        default=None,
        description="The updated description of the field, if any",
    )


class InputFieldUpdates(BaseModel):
    field_updates: List[InputFieldUpdate] = Field(description="The list of input field updates to apply")


class OutputFieldUpdate(InputFieldUpdate):
    updated_examples: list[str] | None = Field(
        default=None,
        description="The updated examples of the field, if any",
    )


class OutputFieldUpdates(BaseModel):
    field_updates: List[OutputFieldUpdate] = Field(description="The list of output field updates to apply")


def _are_examples_authorized_for_field(field_schema: dict[str, Any]) -> bool:
    if field_schema.get("type") == "string" and field_schema.get("format") is None:
        return True  # Examples are only allowed for bare strings (not for HTML, etc.)
    return False


def _update_field_schema(field_schema: dict[str, Any], update: InputFieldUpdate | OutputFieldUpdate) -> None:
    """Update a field schema with input field update (description only)."""
    if update.updated_description is not None:
        field_schema["description"] = update.updated_description

    if (
        isinstance(update, OutputFieldUpdate)
        and update.updated_examples is not None
        and _are_examples_authorized_for_field(field_schema)
    ):
        field_schema["examples"] = update.updated_examples


def _update_field_in_defs(schema: JsonSchema, update: InputFieldUpdate | OutputFieldUpdate) -> None:
    """Update a field directly in the $defs section for input updates."""
    current_schema = schema.schema
    keys = update.keypath.split(".")

    for key in keys:
        if key not in current_schema:
            raise KeyError(f"Invalid keypath '{update.keypath}': Key {key} not found in object schema")
        current_schema = current_schema[key]  # type: ignore[reportUnknownVariable]

    _update_field_schema(cast(dict[str, Any], current_schema), update)


def _update_field_through_refs(schema: JsonSchema, update: InputFieldUpdate | OutputFieldUpdate) -> None:
    """Update a field by following references for input updates."""
    keys = update.keypath.split(".")
    try:
        field_schema = schema.sub_schema(keys, follow_refs=True)
    except InvalidSchemaError as e:
        raise KeyError(f"Invalid keypath '{update.keypath}': {e}") from e

    _update_field_schema(cast(dict[str, Any], field_schema.schema), update)


def apply_field_updates(
    json_schema: RawJsonSchema | dict[str, Any],
    field_updates: list[InputFieldUpdate] | list[OutputFieldUpdate],
) -> dict[str, Any]:
    """Apply input field updates to a JSON schema.

    Args:
        json_schema: The JSON schema to update
        field_updates: List of input field updates to apply

    Returns:
        The updated JSON schema
    """
    schema = JsonSchema(json_schema)

    for update in field_updates:
        if update.keypath.startswith("$defs."):
            _update_field_in_defs(schema, update)
        else:
            _update_field_through_refs(schema, update)

    return cast(dict[str, Any], schema.schema)
