from typing import Any

import pytest

from core.domain.fields.file import File
from core.domain.task_typology import TaskTypology


class TestTypologyFromSchema:
    def test_no_file(self):
        schema = {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
            },
        }
        typology = TaskTypology.from_schema(schema)
        assert typology.has_image_in_input is False
        assert typology.has_multiple_images_in_input is False
        assert typology.has_audio_in_input is False

    def test_image_in_input(self):
        schema = {
            "type": "object",
            "properties": {"image": {"$ref": "#/$defs/File", "format": "image"}},
            "$defs": {"File": File.model_json_schema()},
        }
        typology = TaskTypology.from_schema(schema)
        assert typology.has_image_in_input is True
        assert typology.has_multiple_images_in_input is False
        assert typology.has_audio_in_input is False

    def test_deprecated_image_in_input(self):
        schema = {
            "type": "object",
            "properties": {"image": {"$ref": "#/$defs/Image"}},
            "$defs": {"Image": File.model_json_schema()},
        }
        typology = TaskTypology.from_schema(schema)
        assert typology.has_image_in_input is True
        assert typology.has_multiple_images_in_input is False
        assert typology.has_audio_in_input is False

    def test_array_of_images_in_input(self):
        schema = {
            "type": "object",
            "properties": {"images": {"type": "array", "items": {"$ref": "#/$defs/Image"}}},
            "$defs": {"Image": File.model_json_schema()},
        }
        typology = TaskTypology.from_schema(schema)
        assert typology.has_image_in_input is True
        assert typology.has_multiple_images_in_input is True
        assert typology.has_audio_in_input is False

    @pytest.mark.parametrize(
        "schema, expected",
        [
            ({"$defs": {"File": {}}}, False),
            (
                {
                    "$defs": {"File": {}},
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                            },
                        },
                    },
                },
                False,
            ),
            (
                {
                    "$defs": {"File": {}},
                    "type": "array",
                    "items": {
                        "$ref": "#/$defs/File",
                        "format": "image",
                    },
                },
                True,
            ),
            (
                {
                    "$defs": {"File": {}},
                    "type": "array",
                    "items": {
                        "$ref": "#/$defs/File",
                        "format": "audio",
                    },
                },
                False,
            ),
            (
                {
                    "$defs": {"File": {}},
                    "type": "object",
                    "properties": {
                        "nested_array": {"type": "array", "items": {"$ref": "#/$defs/File", "format": "image"}},
                    },
                },
                True,
            ),
            ({"$defs": {"Image": {}}}, False),
            (
                {
                    "$defs": {"File": {}},
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                            },
                        },
                    },
                },
                False,
            ),
            # Array at root
            (
                {
                    "$defs": {"Image": {}},
                    "type": "array",
                    "items": {
                        "$ref": "#/$defs/Image",
                    },
                },
                True,
            ),
            # Array as a property
            (
                {
                    "$defs": {"Image": {}},
                    "type": "object",
                    "properties": {
                        "nested_array": {"type": "array", "items": {"$ref": "#/$defs/Image"}},
                    },
                },
                True,
            ),
            # 2 images as properties
            (
                {
                    "$defs": {"Image": {}},
                    "type": "object",
                    "properties": {
                        "image1": {"$ref": "#/$defs/Image"},
                        "image2": {"$ref": "#/$defs/Image"},
                    },
                },
                True,
            ),
        ],
    )
    def test_has_array_of_images(self, schema: dict[str, Any], expected: bool):
        typology = TaskTypology.from_schema(schema)
        assert typology.has_multiple_images_in_input == expected
