from typing import Any

import pytest
from datamodel_code_generator.imports import Import

from core.utils.schemas import JsonSchema, RawJsonSchema

from .schema_to_task import (
    SpecialTypes,
    _parse_imports,  # type: ignore
    format_object,
    is_type_used_in_code,
    remove_title,
    replace_special_types,
    schema_to_task_example,
    schema_to_task_io,
    schema_to_task_models,
)


@pytest.fixture(params=["File", "Image"])
def parameterized_schema(request: pytest.FixtureRequest) -> dict[str, Any]:
    return {
        "description": "JSON schema for extracting physical locations and time for a calendar event",
        "type": "object",
        "properties": {
            "event_description": {
                "type": "string",
                "description": "The full description of the calendar event from which to extract the data",
                "examples": ["An event description example"],
            },
            "event_start_time": {
                "$ref": "#/$defs/DatetimeLocal",
                "description": "The start time of the event including the timezone information",
            },
            "event_image": {
                "$ref": f"#/$defs/{request.param}",
                "description": f"The {request.param.lower()} of the event",
            },
        },
        "required": ["event_description", "event_start_time", "event_image"],
        "defs": {
            "DatetimeLocal": {"type": "object"},
            "File": {"type": "object"},
            "Image": {"type": "object"},
        },
    }


schema_without_datetime_local = {
    "description": "JSON schema for extracting physical locations and time for a calendar event",
    "type": "object",
    "properties": {"image": {"$ref": "#/$defs/File"}},
    "required": ["image"],
}

description = "Example task description"

instructions = """Example task instuctions"""


@pytest.mark.parametrize(
    "str, expected",
    [
        ("import pydantic", [Import(import_="pydantic")]),
        ("from pydantic import BaseModel", [Import(from_="pydantic", import_="BaseModel")]),
        (
            "from pydantic import BaseModel, Field",
            [Import(from_="pydantic", import_="BaseModel"), Import(from_="pydantic", import_="Field")],
        ),
    ],
)
def test_parse_imports(str: str, expected: list[Import]) -> None:
    assert _parse_imports(str) == expected


class TestSchemaToTaskIO:
    def test_schema_to_task_io(self, parameterized_schema: dict[str, Any]) -> None:
        file_type = parameterized_schema["properties"]["event_image"]["$ref"].split("/")[-1]
        expected = f"""class SomeInput(BaseModel):
    event_description: str
    event_start_time: DatetimeLocal
    event_image: {file_type}"""
        created = schema_to_task_io("SomeInput", parameterized_schema, "BaseModel")[0]

        assert created == expected

    def test_with_list(self):
        schema = {
            "type": "object",
            "properties": {
                "List": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "flavor_profile": {
                    "type": "string",
                },
                "Dict": {
                    "type": "object",
                },
            },
        }
        created = schema_to_task_io("SomeInput", schema, "BaseModel")[0]
        expected = """class SomeInput(BaseModel):
    List: Optional[list[str]] = None
    flavor_profile: Optional[str] = None
    Dict: Optional[dict[str, Any]] = None"""
        assert created == expected


class TestSchemaToTask:
    def test_schema_to_task(self, parameterized_schema: dict[str, Any]) -> None:
        file_type = parameterized_schema["properties"]["event_image"]["$ref"].split("/")[-1]
        expected = f"""class SomeInput(BaseModel):
    event_description: str
    event_start_time: DatetimeLocal
    event_image: {file_type}

class SomeOutput(BaseModel):
    event_description: str
    event_start_time: DatetimeLocal
    event_image: {file_type}"""

        created = schema_to_task_models(
            "SomeTask",
            input_schema=parameterized_schema,
            output_schema=parameterized_schema,
        )

        assert created[0] == expected
        assert (
            created[1].dump()
            == f"""from pydantic import BaseModel
from workflowai.fields import DatetimeLocal, {file_type}"""
        )

    def test_schema_to_task_without_datetime_local(self) -> None:
        expected = """class SomeInput(BaseModel):
    image: File

class SomeOutput(BaseModel):
    image: File"""

        created = schema_to_task_models("SomeTask", schema_without_datetime_local, schema_without_datetime_local)

        # Spaces are removed to ignore minor differences in and spaces
        assert created[0] == expected
        assert (
            created[1].dump()
            == """from pydantic import BaseModel
from workflowai.fields import File"""
        )

    @pytest.mark.parametrize("name, expected", [("001Some001Task", "Some001"), ("001Some001Task001", "Some001Task001")])
    def test_schema_to_task_with_leading_number(
        self,
        parameterized_schema: dict[str, Any],
        name: str,
        expected: str,
    ) -> None:
        file_type = parameterized_schema["properties"]["event_image"]["$ref"].split("/")[-1]
        expected = f"""class {expected}Input(BaseModel):
    event_description: str
    event_start_time: DatetimeLocal
    event_image: {file_type}

class {expected}Output(BaseModel):
    event_description: str
    event_start_time: DatetimeLocal
    event_image: {file_type}"""

        created = schema_to_task_models(
            name,
            input_schema=parameterized_schema,
            output_schema=parameterized_schema,
        )

        assert created[0] == expected
        assert (
            created[1].dump()
            == f"""from pydantic import BaseModel
from workflowai.fields import DatetimeLocal, {file_type}"""
        )


def test_confloat_is_not_used() -> None:
    # Test that 'float' is used instead of 'confloat'
    # Test that 'ge' and 'le' are well set

    schema = {
        "description": "JSON schema that contains a float",
        "type": "object",
        "properties": {
            "probability": {
                "type": "number",
                "maximum": 1.0,
                "minimum": 0.0,
            },
        },
        "required": ["probability"],
    }

    task_definition = schema_to_task_models("SomeTask", schema, schema)[0]

    assert "confloat" not in task_definition
    assert ": float = Field(ge=0.0, le=1.0)" in task_definition


def test_replace_special_types_replaces_timezone() -> None:
    prop = {"type": "string", "format": "timezone"}
    replace_special_types(prop)
    assert prop == {"allOf": [{"$ref": "#/$defs/TimezoneInfo"}]}


def test_replace_special_types_replaces_special_json_type() -> None:
    prop = {"type": "string", "format": "html"}
    replace_special_types(prop)
    assert prop == {"allOf": [{"$ref": "#/$defs/HTMLString"}]}


def test_replace_special_types_does_not_replace_regular_json_type() -> None:
    prop = {"type": "string"}
    replace_special_types(prop)
    assert prop == {"type": "string"}


def test_remove_title_removes_title() -> None:
    prop = {"type": "string", "title": "Some title"}
    remove_title(prop)
    assert prop == {"type": "string"}


def test_is_type_used_in_code_False() -> None:
    # Check 'is_type_used_in_code' work for very simple cases

    code = """
class Input(BaseModel):
   field_1: str = Field(description="Field 1")

class Output(BaseModel):
   field_2: str = Field(description="Field 2")

"""

    special_type = SpecialTypes.File

    assert is_type_used_in_code(special_type, code) is False


def test_is_type_used_in_code_False_2() -> None:
    # Check 'is_type_used_in_code' work for confusing cases: 'AntherImageType'
    # as well as 'File' as part of a description

    code = """
class Input(BaseModel):
   field_1: AntherFileType = Field(description="Field 1")

class Output(BaseModel):
   field_2: str = Field(description="File")
"""

    special_type = SpecialTypes.File

    assert is_type_used_in_code(special_type, code) is False


def test_is_type_used_in_code_True() -> None:
    code = """

class Input(BaseModel):
   field_1: File = Field(description="Field 1")

class Output(BaseModel):
   field_2: str = Field(description="File")
"""

    special_type = SpecialTypes.File

    assert is_type_used_in_code(special_type, code) is True


def test_is_type_used_in_code_True_list() -> None:
    code = """
class Input(BaseModel):
   field_1: list[File] = Field(description="Field 1")

class Output(BaseModel):
   field_2: str = Field(description="File")
"""

    special_type = SpecialTypes.File

    assert is_type_used_in_code(special_type, code) is True


def test_is_type_used_in_code_False_with_schema_to_task_io(parameterized_schema: dict[str, Any]) -> None:
    code = schema_to_task_io("SomeInput", parameterized_schema, "BaseModel")[0]

    special_type = SpecialTypes.HTMLString

    assert is_type_used_in_code(special_type, code) is False


def test_is_type_used_in_code_True_with_schema_to_task_io(parameterized_schema: dict[str, Any]) -> None:
    code = schema_to_task_io("SomeInput", parameterized_schema, "BaseModel")[0]

    special_type = (
        SpecialTypes.File
        if "File" in parameterized_schema["properties"]["event_image"]["$ref"].split("/")[-1]
        else SpecialTypes.Image
    )

    assert is_type_used_in_code(special_type, code) is True


def test_simple_schema():
    input_schema = JsonSchema(
        {
            "type": "object",
            "properties": {
                "sender": {"description": "The email address of the sender", "type": "string"},
                "recipient": {"description": "The email address of the recipient", "type": "string"},
            },
            "title": "SenderInput",
        },
    )

    result = schema_to_task_example(
        input_schema,
        {"sender": "spatika@workflowai.com", "recipient": "spatika1@workflowai.com"},
    )
    assert (
        result
        == """SenderInput(
    sender='spatika@workflowai.com',
    recipient='spatika1@workflowai.com',
)"""
    )


def test_schema_to_task_input_indented():
    input_schema = RawJsonSchema(
        {
            "type": "object",
            "properties": {
                "email_conversation": {
                    "description": "An array of email messages in the conversation",
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sender": {"description": "The email address of the sender", "type": "string"},
                            "recipient": {"description": "The email address of the recipient", "type": "string"},
                            "subject": {"description": "The subject line of the email", "type": "string"},
                            "body": {"description": "The main content of the email", "type": "string"},
                            "timestamp": {
                                "title": "DatetimeLocal",
                                "type": "object",
                                "properties": {
                                    "date": {"title": "Date", "type": "string", "format": "date"},
                                    "local_time": {"title": "Local Time", "type": "string", "format": "time"},
                                    "timezone": {"title": "Timezone", "type": "string", "format": "timezone"},
                                },
                            },
                        },
                    },
                },
            },
            "title": "EmailConversationInput",
        },
    )
    jsonschemaObject = JsonSchema(schema=input_schema)
    example_input = {
        "email_conversation": [
            {
                "sender": "spatika@workflowai.com",
                "recipient": "spatika@workflowai.com",
                "subject": "TestingFeature",
                "body": "This is a feature testing and of okayish importance.",
                "timestamp": {
                    "date": "2024-09-12",
                    "local_time": "12:05:00",
                    "timezone": "America/New_York",
                },
            },
        ],
    }

    result = schema_to_task_example(jsonschemaObject, example_input)
    expected = """EmailConversationInput(
    email_conversation=[
        EmailConversation(
            sender='spatika@workflowai.com',
            recipient='spatika@workflowai.com',
            subject='TestingFeature',
            body='This is a feature testing and of okayish importance.',
            timestamp=DatetimeLocal(
                date='2024-09-12',
                local_time='12:05:00',
                timezone='America/New_York',
            ),
        ),
    ],
)"""
    assert result == expected


def test_format_object():
    example_input = {
        "correct_outputs": [
            "Contact Carl about upstairs bathroom damages",
        ],
        "evaluated_output": "Reach out to Project Manager Carl",
        "evaluation_result": True,
        "incorrect_outputs": [],
        "user_feedback": "The output doesn't match exactly the correct output. ",
        "only_one_list_item": [
            "only_one_list_item",
        ],
        "two_list_items": [
            "two_list_items1",
            "two_list_items2",
        ],
    }
    properties_schema = JsonSchema(
        {
            "type": "object",
            "properties": {
                "correct_outputs": {"type": "array", "items": {"type": "string"}},
                "evaluated_output": {"type": "string"},
                "evaluation_result": {"type": "boolean"},
                "incorrect_outputs": {"type": "array", "items": {"type": "string"}},
                "user_feedback": {"type": "string"},
                "only_one_list_item": {"type": "array", "items": {"type": "string"}},
                "two_list_items": {"type": "array", "items": {"type": "string"}},
            },
        },
    )
    result = format_object("ExampleInput", example_input, properties_schema, 0, [])
    expected = """ExampleInput(
    correct_outputs=['Contact Carl about upstairs bathroom damages'],
    evaluated_output='Reach out to Project Manager Carl',
    evaluation_result=True,
    incorrect_outputs=[],
    user_feedback="The output doesn't match exactly the correct output. ",
    only_one_list_item=['only_one_list_item'],
    two_list_items=[
        'two_list_items1',
        'two_list_items2',
    ],
)"""
    assert result == expected


def test_format_image():
    raw_schema = JsonSchema(
        {
            "type": "object",
            "properties": {"image": {"$ref": "#/$defs/Image"}},
            "$defs": {
                "Image": {
                    "properties": {
                        "content_type": {
                            "default": "",
                            "description": "The content type of the file",
                            "examples": ["image/png", "image/jpeg", "audio/wav", "application/pdf"],
                            "title": "Content Type",
                            "type": "string",
                        },
                        "data": {
                            "anyOf": [{"type": "string"}, {"type": "null"}],
                            "description": "The base64 encoded data of the file",
                            "title": "Data",
                        },
                        "url": {
                            "anyOf": [{"type": "string"}, {"type": "null"}],
                            "description": "The URL of the image",
                            "title": "Url",
                        },
                    },
                    "title": "File",
                    "type": "object",
                },
            },
            "title": "CountDogsInImageInput",
        },
    )
    example_input = {
        "image": {
            "url": "https://images.pexels.com/photos/1108099/pexels-photo-1108099.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
        },
    }

    result = schema_to_task_example(raw_schema, example_input)
    assert (
        result
        == """CountDogsInImageInput(
    image=Image(
        url='https://images.pexels.com/photos/1108099/pexels-photo-1108099.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2',
    ),
)"""
    )
