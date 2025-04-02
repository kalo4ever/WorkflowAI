import unittest
from typing import Any

import pytest

from core.agents.chat_task_schema_generation.apply_field_updates import (
    InputFieldUpdate,
    OutputFieldUpdate,
    apply_field_updates,
)


class TestApplyFieldUpdates:
    @pytest.fixture
    def json_schema(self):
        return {
            "type": "object",
            "$defs": {
                "Item": {
                    "type": "object",
                    "properties": {
                        "item_name": {
                            "type": "string",
                            "description": "Name of the item",
                            "examples": ["Sword", "Shield"],
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Number of items",
                        },
                    },
                },
                "status_info": {
                    "type": "object",
                    "properties": {
                        "state": {
                            "type": "string",
                            "description": "Current state of the player",
                            "examples": ["active", "inactive"],
                        },
                        "string_field": {
                            "type": "string",
                            "description": "Status start time",
                            "examples": ["some string"],
                        },
                    },
                },
            },
            "properties": {
                "player": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the player.",
                            "examples": ["Alice", "Bob"],
                        },
                        "score": {
                            "type": "integer",
                            "description": "The score of the player.",
                        },
                        "inventory": {
                            "type": "array",
                            "description": "Player's inventory items",
                            "items": {
                                "$ref": "#/$defs/Item",
                            },
                        },
                        "status": {
                            "description": "Player's current status",
                            "anyOf": [
                                {
                                    "$ref": "#/$defs/status_info",
                                },
                                {
                                    "type": "null",
                                },
                            ],
                        },
                        "equipped_item": {
                            "$ref": "#/$defs/Item",
                            "description": "Currently equipped item",
                        },
                        "field_with_no_examples": {
                            "type": "string",
                        },
                        "some_html_field": {
                            "type": "string",
                            "format": "html",
                        },
                    },
                },
            },
        }

    def test_input_update_description(self, json_schema: dict[str, Any]):
        field_updates = [
            InputFieldUpdate(
                keypath="player.name",
                updated_description="The full name of the player.",
            ),
        ]
        updated_schema = apply_field_updates(json_schema, field_updates)
        assert (
            updated_schema["properties"]["player"]["properties"]["name"]["description"]
            == "The full name of the player."
        )

    def test_output_update_examples_on_non_string_field(self, json_schema: dict[str, Any]):
        field_updates = [
            OutputFieldUpdate(keypath="player.score", updated_description=None, updated_examples=["30", "40"]),
        ]
        updated_schema = apply_field_updates(json_schema, field_updates)
        assert "examples" not in updated_schema["properties"]["player"]["properties"]["score"]  # update is rejected

    def test_output_update_both_fields(self, json_schema: dict[str, Any]):
        field_updates = [
            OutputFieldUpdate(
                keypath="player.name",
                updated_description="Player's display name.",
                updated_examples=["Charlie", "Dana"],
            ),
        ]
        updated_schema = apply_field_updates(json_schema, field_updates)
        name_schema = updated_schema["properties"]["player"]["properties"]["name"]
        assert name_schema["description"] == "Player's display name."
        assert name_schema["examples"] == ["Charlie", "Dana"]

    def test_input_invalid_keypath(self, json_schema: dict[str, Any]):
        field_updates = [
            InputFieldUpdate(
                keypath="player.age",
                updated_description="The age of the player.",
            ),
        ]
        with pytest.raises(KeyError):
            apply_field_updates(json_schema, field_updates)

    def test_output_invalid_keypath(self, json_schema: dict[str, Any]):
        field_updates = [
            OutputFieldUpdate(
                keypath="player.age",
                updated_description="The age of the player.",
                updated_examples=None,
            ),
        ]
        with pytest.raises(KeyError):
            apply_field_updates(json_schema, field_updates)

    def test_input_update_array_item_description(self, json_schema: dict[str, Any]):
        """Test updating description of a field within an array item"""
        field_updates = [
            InputFieldUpdate(
                keypath="player.inventory.0.item_name",
                updated_description="Name of the inventory item",
            ),
        ]
        updated_schema = apply_field_updates(json_schema, field_updates)
        assert updated_schema["$defs"]["Item"]["properties"]["item_name"]["description"] == "Name of the inventory item"

    def test_output_update_anyof_field(self, json_schema: dict[str, Any]):
        """Test updating a field within an anyOf structure"""
        field_updates = [
            OutputFieldUpdate(
                keypath="player.status.state",
                updated_description="Current player state",
                updated_examples=["online", "offline"],
            ),
        ]
        updated_schema = apply_field_updates(json_schema, field_updates)
        status_schema = updated_schema["$defs"]["status_info"]
        assert status_schema["properties"]["state"]["description"] == "Current player state"
        assert status_schema["properties"]["state"]["examples"] == ["online", "offline"]

    def test_output_multiple_nested_updates(self, json_schema: dict[str, Any]):
        """Test multiple updates at different nesting levels"""
        field_updates = [
            OutputFieldUpdate(
                keypath="player.inventory.0.quantity",
                updated_description="Amount of items owned",
                updated_examples=["10", "20"],  # update must be rejected, because quantity is an integer
            ),
            OutputFieldUpdate(
                keypath="player.status.string_field",
                updated_description="Timestamp of status change",
                updated_examples=["some other string"],
            ),
        ]
        updated_schema = apply_field_updates(json_schema, field_updates)

        # Check inventory quantity update
        quantity_schema = updated_schema["$defs"]["Item"]["properties"]["quantity"]
        assert quantity_schema["description"] == "Amount of items owned"
        assert "examples" not in quantity_schema  # update is rejected

        # Check status timestamp update
        status_schema = updated_schema["$defs"]["status_info"]
        assert status_schema["properties"]["string_field"]["description"] == "Timestamp of status change"
        assert status_schema["properties"]["string_field"]["examples"] == ["some other string"]

    def test_input_invalid_array_path(self, json_schema: dict[str, Any]):
        """Test invalid path within array structure"""
        field_updates = [
            InputFieldUpdate(
                keypath="player.inventory.items.invalid_field",
                updated_description="This should fail",
            ),
        ]
        with pytest.raises(KeyError):
            apply_field_updates(json_schema, field_updates)

    def test_output_invalid_array_path(self, json_schema: dict[str, Any]):
        """Test invalid path within array structure"""
        field_updates = [
            OutputFieldUpdate(
                keypath="player.inventory.items.invalid_field",
                updated_description="This should fail",
                updated_examples=None,
            ),
        ]
        with pytest.raises(KeyError):
            apply_field_updates(json_schema, field_updates)

    def test_input_invalid_anyof_path(self, json_schema: dict[str, Any]):
        """Test invalid path within anyOf structure"""
        field_updates = [
            InputFieldUpdate(
                keypath="player.status.invalid_field",
                updated_description="This should fail",
            ),
        ]
        with pytest.raises(KeyError):
            apply_field_updates(json_schema, field_updates)

    def test_output_invalid_anyof_path(self, json_schema: dict[str, Any]):
        """Test invalid path within anyOf structure"""
        field_updates = [
            OutputFieldUpdate(
                keypath="player.status.invalid_field",
                updated_description="This should fail",
                updated_examples=None,
            ),
        ]
        with pytest.raises(KeyError):
            apply_field_updates(json_schema, field_updates)

    def test_input_update_ref_in_defs(self, json_schema: dict[str, Any]):
        """Test updating a field in $defs that's referenced multiple times"""
        field_updates = [
            InputFieldUpdate(
                keypath="$defs.Item.properties.item_name",
                updated_description="Updated item name description",
            ),
        ]
        updated_schema = apply_field_updates(json_schema, field_updates)

        # Check the definition was updated
        item_def = updated_schema["$defs"]["Item"]["properties"]["item_name"]
        assert item_def["description"] == "Updated item name description"

    def test_output_update_ref_in_defs(self, json_schema: dict[str, Any]):
        """Test updating a field in $defs that's referenced multiple times"""
        field_updates = [
            OutputFieldUpdate(
                keypath="$defs.Item.properties.item_name",
                updated_description="Updated item name description",
                updated_examples=["Axe", "Bow"],
            ),
        ]
        updated_schema = apply_field_updates(json_schema, field_updates)

        # Check the definition was updated
        item_def = updated_schema["$defs"]["Item"]["properties"]["item_name"]
        assert item_def["description"] == "Updated item name description"
        assert item_def["examples"] == ["Axe", "Bow"]

    def test_output_update_through_ref(self, json_schema: dict[str, Any]):
        """Test updating a field by accessing it through a $ref"""
        field_updates = [
            OutputFieldUpdate(
                keypath="player.equipped_item.item_name",
                updated_description="Name of the equipped item",
                updated_examples=["Dragon Sword"],
            ),
        ]
        updated_schema = apply_field_updates(json_schema, field_updates)

        # The update should modify the original definition
        item_def = updated_schema["$defs"]["Item"]["properties"]["item_name"]
        assert item_def["description"] == "Name of the equipped item"
        assert item_def["examples"] == ["Dragon Sword"]

    def test_input_update_through_ref(self, json_schema: dict[str, Any]):
        """Test updating a field by accessing it through a $ref"""
        field_updates = [
            InputFieldUpdate(
                keypath="player.equipped_item.item_name",
                updated_description="Name of the equipped item",
            ),
        ]
        updated_schema = apply_field_updates(json_schema, field_updates)

        # The update should modify the original definition
        item_def = updated_schema["$defs"]["Item"]["properties"]["item_name"]
        assert item_def["description"] == "Name of the equipped item"

    def test_output_update_array_with_ref(self, json_schema: dict[str, Any]):
        """Test updating a field in an array that uses $ref"""
        field_updates = [
            OutputFieldUpdate(
                keypath="player.inventory.0.quantity",
                updated_description="Amount in inventory",
                updated_examples=["100", "200"],
            ),
        ]
        updated_schema = apply_field_updates(json_schema, field_updates)

        # Check that the definition was updated
        quantity_def = updated_schema["$defs"]["Item"]["properties"]["quantity"]
        assert quantity_def["description"] == "Amount in inventory"
        assert "examples" not in quantity_def

    def test_input_update_array_with_ref(self, json_schema: dict[str, Any]):
        """Test updating a field in an array that uses $ref"""
        field_updates = [
            InputFieldUpdate(
                keypath="player.inventory.0.quantity",
                updated_description="Amount in inventory",
            ),
        ]
        updated_schema = apply_field_updates(json_schema, field_updates)

        # Check that the definition was updated
        quantity_def = updated_schema["$defs"]["Item"]["properties"]["quantity"]
        assert quantity_def["description"] == "Amount in inventory"

    def test_output_update_anyof_with_ref(self, json_schema: dict[str, Any]):
        """Test updating a field in anyOf that uses $ref"""
        field_updates = [
            OutputFieldUpdate(
                keypath="player.status.state",
                updated_description="Player's current state",
                updated_examples=["playing", "resting"],
            ),
        ]
        updated_schema = apply_field_updates(json_schema, field_updates)

        # Check that the definition was updated
        state_def = updated_schema["$defs"]["status_info"]["properties"]["state"]
        assert state_def["description"] == "Player's current state"
        assert state_def["examples"] == ["playing", "resting"]

    def test_input_update_anyof_with_ref(self, json_schema: dict[str, Any]):
        """Test updating a field in anyOf that uses $ref"""
        field_updates = [
            InputFieldUpdate(
                keypath="player.status.state",
                updated_description="Player's current state",
            ),
        ]
        updated_schema = apply_field_updates(json_schema, field_updates)

        # Check that the definition was updated
        state_def = updated_schema["$defs"]["status_info"]["properties"]["state"]
        assert state_def["description"] == "Player's current state"

    def test_input_invalid_ref_path(self, json_schema: dict[str, Any]):
        """Test invalid path when using $ref"""
        field_updates = [
            InputFieldUpdate(
                keypath="$defs.nonexistent.field",
                updated_description="This should fail",
            ),
        ]
        with pytest.raises(KeyError):
            apply_field_updates(json_schema, field_updates)

    def test_output_invalid_ref_path(self, json_schema: dict[str, Any]):
        """Test invalid path when using $ref"""
        field_updates = [
            OutputFieldUpdate(
                keypath="$defs.nonexistent.field",
                updated_description="This should fail",
                updated_examples=None,
            ),
        ]
        with pytest.raises(KeyError):
            apply_field_updates(json_schema, field_updates)

    def test_output_adding_examples_and_description_empty_before(self, json_schema: dict[str, Any]):
        field_updates = [
            OutputFieldUpdate(
                keypath="player.field_with_no_examples",
                updated_description="",
                updated_examples=["1", "2"],
            ),
        ]
        updated_schema = apply_field_updates(json_schema, field_updates)
        assert updated_schema["properties"]["player"]["properties"]["field_with_no_examples"]["description"] == ""
        assert updated_schema["properties"]["player"]["properties"]["field_with_no_examples"]["examples"] == ["1", "2"]

    def test_output_update_examples_on_html_field(self, json_schema: dict[str, Any]):
        field_updates = [
            OutputFieldUpdate(
                keypath="player.some_html_field",
                updated_description="updated HTML field description",
                updated_examples=["<p>some html</p>"],
            ),
        ]
        updated_schema = apply_field_updates(json_schema, field_updates)
        assert (
            updated_schema["properties"]["player"]["properties"]["some_html_field"]["description"]
            == "updated HTML field description"  # description update is accepted
        )
        assert (
            "examples" not in updated_schema["properties"]["player"]["properties"]["some_html_field"]
        )  # example update is rejected


if __name__ == "__main__":
    unittest.main()
