import json
import re
from copy import deepcopy
from enum import Enum
from typing import Any, cast

from datamodel_code_generator import DataModelType, PythonVersion
from datamodel_code_generator.imports import IMPORT_ANNOTATIONS, Import, Imports
from datamodel_code_generator.model import get_data_model_types
from datamodel_code_generator.parser.jsonschema import JsonSchemaParser

from core.utils import strings
from core.utils.schemas import JsonSchema, strip_metadata


class SpecialTypes(str, Enum):
    """
    Here are defined the special types to use in the JSON schema, based on the poperties 'format'.

    Those may, or may not be offical JSON schema types.

    For example, 'email' is not an official JSON schema type, but we chose to use our custom 'EmailAddressStr' type instead of Pydantic's 'EmailStr'.
    Opposingly, 'html' is not an official JSON schema type, and we have a special type for it, 'HTMLString'.

    To add new types, add a new enum member, update '_IMPORT_MAP' and 'JSON_FORMAT_TO_SPECIAL_TYPE_MAP' accordingly.
    """

    DatetimeLocal = "DatetimeLocal"
    HTMLString = "HTMLString"
    TimezoneInfo = "TimezoneInfo"
    EmailAddressStr = "EmailAddressStr"
    datetime = "datetime"
    HttpUrl = "HttpUrl"
    File = "File"
    Image = "Image"
    Audio = "Audio"
    PDF = "PDF"

    def import_path(self) -> str:
        _IMPORT_MAP = {
            self.DatetimeLocal: "workflowai.fields.DatetimeLocal",
            self.HTMLString: "workflowai.fields.HTMLString",
            self.TimezoneInfo: "workflowai.fields.TimezoneInfo",
            self.EmailAddressStr: "workflowai.fields.EmailAddressStr",
            self.datetime: "datetime.datetime",
            self.HttpUrl: "workflowai.fields.HttpUrl",
            self.File: "workflowai.fields.File",
            self.Image: "workflowai.fields.Image",
            self.Audio: "workflowai.fields.Audio",
            self.PDF: "workflowai.fields.PDF",
        }

        return _IMPORT_MAP[self]


JSON_FORMAT_TO_SPECIAL_TYPE_MAP: dict[str, SpecialTypes] = {
    "html": SpecialTypes.HTMLString,
    "timezone": SpecialTypes.TimezoneInfo,
    "email": SpecialTypes.EmailAddressStr,
    "date-time": SpecialTypes.datetime,
    "url": SpecialTypes.HttpUrl,
    "uri": SpecialTypes.HttpUrl,
}


def _is_import_line(line: str, add_to_imports: set[str]) -> bool:
    if line.startswith("from") or line.startswith("import"):
        add_to_imports.add(line)
        return True
    return False


def _parse_imports(line: str) -> list[Import]:
    if line.startswith("from"):
        parts = line[5:].split(" import ")
        return [Import(from_=parts[0], import_=split.strip()) for split in parts[1].split(",")]
    parts = line.split(" ")
    return [Import(import_=parts[1])]


def _remove_all_imports(imports: Imports, import_: Import) -> None:
    if (import_.from_, import_.import_) in imports.counter:
        del imports.counter[(import_.from_, import_.import_)]

    try:
        imports[import_.from_].remove(import_.import_)
        if not imports[import_.from_]:
            del imports[import_.from_]
    except KeyError:
        pass

    if import_.alias:
        try:
            del imports.alias[import_.from_][import_.import_]
            if not imports.alias[import_.from_]:
                del imports.alias[import_.from_]
        except KeyError:
            pass


def prepare_properties(properties: dict[str, Any]):
    for prop in properties.values():
        replace_special_types(prop)

        # Remove title from properties, as we are only using 'description'
        remove_title(prop)


def remove_title(prop: dict[str, Any]):
    if "title" in prop:
        del prop["title"]


def replace_special_types(prop: dict[str, Any]):
    """
    Replace special json types, ex: {"format": "html"}
    with their corresponding $defs in the schema, ex: {"allOf": [{"$ref": "#/$defs/HTMLString"}]}
    """

    DEFS_PATH = "#/$defs"

    if prop.get("type") == "string" and prop.get("format") in JSON_FORMAT_TO_SPECIAL_TYPE_MAP:
        new_type = JSON_FORMAT_TO_SPECIAL_TYPE_MAP[prop.get("format")].value  # type: ignore
        prop["allOf"] = [{"$ref": f"{DEFS_PATH}/{new_type}"}]
        del prop["type"]
        del prop["format"]
    elif (
        prop.get("type") == "array"
        and "items" in prop
        and prop["items"].get("type") == "string"
        and prop["items"].get("format") in JSON_FORMAT_TO_SPECIAL_TYPE_MAP
    ):
        new_type = JSON_FORMAT_TO_SPECIAL_TYPE_MAP[prop["items"].get("format")].value
        prop["items"]["$ref"] = f"{DEFS_PATH}/{new_type}"
        del prop["items"]["type"]
        del prop["items"]["format"]


# TODO: Rather check in the schema for the presence of $defs/HTMLString, $defs/TimezoneInfo, etc.
def is_type_used_in_code(special_type: SpecialTypes, code: str) -> bool:
    """Check if a type is used in the generated code."""

    return f": {special_type.value}" in code or f"[{special_type.value}]" in code


def schema_to_task_io(
    name: str,
    schema: dict[str, Any],
    super: str = "BaseModel",
) -> tuple[str, list[Import], list[str]]:
    """Generate the code for a single schema"""
    data_model_types = get_data_model_types(
        DataModelType.PydanticV2BaseModel,
        target_python_version=PythonVersion.PY_311,
    )
    schema = deepcopy(schema)
    schema = strip_metadata(schema, {"description", "examples", "title"})
    schema["title"] = name

    # Add custom objects, replace with a simple number
    if "$defs" not in schema:
        schema["$defs"] = {}

    # Inject special types into the schema where needed
    # (ex: "type": "string", "format": "date-time" will be replaced with "allOf": [{"$ref": "#/$defs/DatetimeLocal"}])
    prepare_properties(schema["properties"])
    for definition in schema.get("$defs", {}).values():
        if "properties" in definition:
            prepare_properties(definition["properties"])

    # Add all special types as $defs in the schema
    schema_str: str = json.dumps(
        schema,
    )  # str version of the schema, in order to easily search for special types existence in it.
    for member in SpecialTypes.__members__.values():
        if member.value in schema_str:
            schema["$defs"][member.value] = {"title": member.value, "type": "string"}

    parser = JsonSchemaParser(
        json.dumps(schema),
        data_model_type=data_model_types.data_model,
        data_model_root_type=data_model_types.root_model,
        data_model_field_type=data_model_types.field_model,
        data_type_manager_type=data_model_types.data_type_manager,
        dump_resolve_reference_action=data_model_types.dump_resolve_reference_action,
        field_constraints=True,
    )

    generated = parser.parse()
    if not isinstance(generated, str):
        raise ValueError("Expected a string")

    # Remove ellipsis (...) from the generated code
    generated = generated.replace("..., ", "")
    generated = generated.replace("...,\n", "")
    generated = generated.replace("                description=", "    description=")

    # Replace 'Datetime' with 'datetime' because the parser mistankenly creates a "class Datetime:"" class
    generated = generated.replace("class Datetime(", "class datetime(")  # Will be deleted in the next step
    generated = generated.replace(": Datetime ", ": datetime ")
    generated = generated.replace(": List[Datetime]", ": List[datetime]")

    # Remove all generated classes that may have been create by the schema_to_task_io function for the special types
    for special_type in SpecialTypes.__members__.values():
        generated = generated.replace(
            f"\nclass {special_type.value}(RootModel[str]):\n    root: str = Field(title='{special_type.value}')\n",
            "",
        )

    # Replace the class name
    generated = generated.replace(f"{name}(BaseModel)", f"{name}({super})")

    # Replace List and Dict with list and dict using word boundaries
    generated = re.sub(r"\bList\[\b", "list[", generated)
    generated = re.sub(r"\bDict\[\b", "dict[", generated)

    # Remove imports
    lines = generated.split("\n")

    idx = 0
    imports = set[str]()
    for line in lines:
        if line and not _is_import_line(line, imports):
            break
        idx += 1

    parsed_imports = [_parse_imports(line) for line in imports]
    model_class_names = [model.reference.name for model in parser.results]

    return (
        "\n".join(lines[idx:]).rstrip(),
        [import_ for imports in parsed_imports for import_ in imports],
        model_class_names,
    )


def schema_to_task_models(name: str, input_schema: dict[str, Any], output_schema: dict[str, Any]):
    """Generates the code for both the task input and output, as well as the necessary imports"""
    name = strings.to_pascal_case(name)  # TODO: remove all unsupported chars
    name = name.removesuffix("Task")
    name = re.sub(r"^\d+", "", name)
    input_name = f"{name}Input"
    output_name = f"{name}Output"

    [input, input_imports, input_model_class_names] = schema_to_task_io(input_name, input_schema, "BaseModel")
    [output, output_imports, output_model_class_names] = schema_to_task_io(output_name, output_schema, "BaseModel")

    imports = Imports()
    imports.append(input_imports)
    imports.append(output_imports)
    _remove_all_imports(imports, IMPORT_ANNOTATIONS)
    _remove_all_imports(imports, Import.from_full_path("pydantic.RootModel"))

    io_code = f"""{input}\n\n{output}"""

    if "Field(" not in io_code:
        _remove_all_imports(imports, Import.from_full_path("pydantic.Field"))

    # Add special types imports
    for special_type in SpecialTypes.__members__.values():
        # If the special type is used in the io code, add the import
        if is_type_used_in_code(special_type=special_type, code=io_code):
            imports.append(Import.from_full_path(special_type.import_path()))

    return io_code, imports, input_name, output_name, input_model_class_names, output_model_class_names


_DEFAULT_INDENT = 4


def format_object(
    name: str,
    obj: dict[str, Any],
    schema: JsonSchema,
    indent: int,
    model_classes: list[str],
) -> str:
    parts: list[str] = []
    for key, value in obj.items():
        prop_schema = schema.safe_child_schema(key)
        formatted_value = format_value(key, value, prop_schema, indent + _DEFAULT_INDENT, model_classes)
        parts.append(f"{' ' * (indent + _DEFAULT_INDENT)}{key}={formatted_value}")

    class_name = strings.to_pascal_case(name)
    if model_classes and class_name not in model_classes:
        singular_name = class_name.rstrip("s")
        if singular_name in model_classes:
            class_name = singular_name

    if len(parts) == 1 and indent == 0:
        return f"{class_name}(\n{' ' * (indent + _DEFAULT_INDENT)}{parts[0].strip()},\n)"
    return f"{class_name}(\n{',\n'.join(parts)},\n{' ' * indent})"


def _pick_quote_style(value: str):
    if "\n" in value:
        return '"""'
    if "'" not in value:
        return "'"
    if '"' not in value:
        return '"'
    return '"""'


def format_list(
    name: str,
    value: list[Any],
    schema: JsonSchema,
    indent: int,
    model_classes: list[str],
) -> str:
    if len(value) == 0:
        return "[]"

    formatted_items = [
        format_value(name, item, schema.safe_child_schema(idx), indent + _DEFAULT_INDENT, model_classes)
        for idx, item in enumerate(value)
    ]
    if len(formatted_items) == 1 and "\n" not in formatted_items[0]:
        return f"[{formatted_items[0]}]"

    return (
        f"[\n{' ' * (indent + _DEFAULT_INDENT)}"
        + f",\n{' ' * (indent + _DEFAULT_INDENT)}".join(formatted_items)
        + f",\n{' ' * indent}]"
    )


def format_value(
    key: str,
    value: Any,
    schema: JsonSchema | None,
    indent: int,
    model_classes: list[str],
) -> str:
    if isinstance(value, str):
        quote_style = _pick_quote_style(value)
        return f"{quote_style}{value}{quote_style}"
    if isinstance(value, (int, float, bool)):
        return str(value)
    if value is None:
        return "None"

    if schema is None:
        return "\n".join(
            [f"{' ' * indent}{line}" for line in json.dumps(value, indent=_DEFAULT_INDENT).splitlines()],
        )
    if isinstance(value, list):
        return format_list(key, cast(list[Any], value), schema, indent, model_classes)
    if isinstance(value, dict):
        return format_object(
            schema.followed_ref_name or schema.title or key,
            cast(dict[str, Any], value),
            schema,
            indent,
            model_classes,
        )

    return str(value)


def schema_to_task_example(
    input_schema: JsonSchema,
    example_input: dict[str, Any],
    name: str = "",
    indent: int = 0,
    model_classes: list[str] = [],
) -> str:
    title = f"{input_schema.title or name}"
    return format_object(
        title,
        example_input,
        input_schema,
        indent,
        model_classes,
    )
