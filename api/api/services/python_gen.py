import json
import logging
import re  # Add this import at the top
from typing import Any, NamedTuple, TypedDict, Unpack

from datamodel_code_generator.imports import Import

from core.domain.task_variant import SerializableTaskVariant
from core.utils.schema_to_task.schema_to_task import schema_to_task_example, schema_to_task_models
from core.utils.schemas import JsonSchema
from core.utils.strings import to_snake_case

logger = logging.getLogger(__name__)


def generate_input_constructor(
    name: str,
    input_schema: dict[str, Any],
    input: dict[str, Any],
    model_classes: list[str],
    indent: int = 4,
) -> str:
    try:
        input_schema["title"] = name
        json_input_schema = JsonSchema(input_schema)
        return schema_to_task_example(json_input_schema, input, name=name, indent=indent, model_classes=model_classes)

    except Exception:
        logger.exception(
            "Failed to generate input constructor",
            extra={
                "input_schema": input_schema,
                "input": input,
                "task_name": name,
            },
        )
        return f"{name}Input(...)"


def prefix_lines(lines: str, prefix: str) -> str:
    return "\n".join([f"{prefix}{line}" for line in lines.split("\n")])


def generate_valid_function_name(original: str) -> str:
    """
    Generate a valid Python function name by removing leading digits from the given string.
    Returns the original string with leading digits removed, or 'func' if the result would be empty.
    """
    # Remove leading digits
    name = re.sub(r"^[\d\s]+", "", original)
    if name == "":
        return "func"

    return name


def _fn_name(name: str) -> str:
    return to_snake_case(generate_valid_function_name(name))


def _task_annotation(fn_name: str, task_id: str, schema_id: int, version: str | int) -> str:
    version = json.dumps(version)
    if fn_name == to_snake_case(task_id):
        return f"@workflowai.agent(schema_id={schema_id}, version={version})"

    return f'@workflowai.agent(id="{task_id}", schema_id={schema_id}, version={version})'


class RunTemplateArgs(TypedDict):
    fn_name: str
    input_name: str
    output_name: str
    task_id: str
    schema_id: int
    version: str | int


def _run_template(**kwargs: Unpack[RunTemplateArgs]) -> str:
    output_name = kwargs["output_name"]
    fn_name = kwargs["fn_name"]
    task_id = kwargs["task_id"]
    schema_id = kwargs["schema_id"]
    version = kwargs["version"]
    input_name = kwargs["input_name"]

    return f"""{_task_annotation(fn_name, task_id, schema_id, version)}
async def {fn_name}(_: {input_name}) -> {output_name}:
    # Leave the function body empty
    ..."""


def _input_str(
    name: str,
    input_schema: dict[str, Any],
    example_input: dict[str, Any],
    secondary_input: dict[str, Any] | None,
    model_classes: list[str],
):
    input_constructor = generate_input_constructor(
        name,
        input_schema=input_schema,
        input=example_input,
        model_classes=model_classes,
    )
    if secondary_input:
        secondary_constructor = generate_input_constructor(
            name,
            input_schema=input_schema,
            input=secondary_input,
            indent=0,
            model_classes=model_classes,
        )
        secondary_input_string = "\n" + prefix_lines(f"agent_input = {secondary_constructor}", "    # ")
    else:
        secondary_input_string = ""

    return f"""    agent_input = {input_constructor}{secondary_input_string}"""


def _prints(var_name: str):
    return f"""
    print("\\n--------\\nOutput:\\n", {var_name}.output, "\\n--------\\n")
    print("Model: ", {var_name}.version.properties.model)
    print("Cost: $", {var_name}.cost_usd)
    print(f"Latency: {{{var_name}.duration_seconds:.2f}}s")"""


def _cache_addr():
    return """        # Cache options:
        # - "auto" (default): returns a cached output only if all conditions are met:
        #   1. A previous run exists with matching version and input
        #   2. Temperature is set to 0
        #   3. No tools are enabled
        # - "always": a cached output is returned when available, regardless
        # of the temperature value or enabled tools
        # - "never": the cache is never used"""


def _run_code_block(input_str: str, **kwargs: Unpack[RunTemplateArgs]) -> str:
    err_print = 'print(f"Failed to run agent. Code: {e.error.code}. Message: {e.error.message}")'

    fn_name = kwargs["fn_name"]

    return f"""{_run_template(**kwargs)}

async def run_with_example():
{input_str}
    try:
{_cache_addr()}
        run = await {fn_name}.run(agent_input, use_cache="auto")
    except WorkflowAIError as e:
        {err_print}
        return
{_prints("run")}

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_with_example())
"""


def _stream_code_block(input_str: str, **kwargs: Unpack[RunTemplateArgs]) -> str:
    err_print = 'print(f"Failed to run agent. Code: {e.error.code}. Message: {e.error.message}")'

    fn_name = kwargs["fn_name"]

    return f"""{_run_template(**kwargs)}

async def run_with_example():
{input_str}
    try:
{_cache_addr()}
        async for chunk in {fn_name}.stream(agent_input, use_cache="auto"):
            # All intermediate chunks contains a partial output
            print(chunk)
    except WorkflowAIError as e:
        {err_print}
        return

    # The last chunk contains the final validated output and additional run information{_prints("chunk")}

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_with_example())
"""


class CodeWithImports(NamedTuple):
    imports: str
    code: str


class RunCode(NamedTuple):
    common: str
    run: CodeWithImports
    stream: CodeWithImports


def _init_code(url: str | None = None) -> str:
    first_lines = """# Initialize the shared client
# Not required if the api key is defined using the WORKFLOWAI_API_KEY environment variable"""

    if url:
        second_line = f'workflowai.init(url="{url}", api_key=os.environ["WORKFLOWAI_API_KEY"])'
    else:
        second_line = '# workflowai.init(api_key=os.environ["WORKFLOWAI_API_KEY"])'

    return f"{first_lines}\n{second_line}"


# Returns the start of the code, the run code and the stream code
def generate_full_run_code(
    task_variant: SerializableTaskVariant,
    example_task_run_input: dict[str, Any],
    version: str | int,
    url: str | None = None,
    secondary_input: dict[str, Any] | None = None,
):
    io_code, imports, input_name, output_name, input_model_class_names, output_model_class_names = (
        schema_to_task_models(
            name=task_variant.name,
            input_schema=task_variant.input_schema.json_schema,
            output_schema=task_variant.output_schema.json_schema,
        )
    )

    # namespace: dict[str, Any] = {}
    # # exec(io_code, namespace)

    model_classes = input_model_class_names + output_model_class_names
    input_str = _input_str(
        input_name,
        task_variant.input_schema.json_schema,
        example_task_run_input or {},
        secondary_input,
        model_classes,
    )
    fn_name = _fn_name(task_variant.name)
    template_args: RunTemplateArgs = {
        "fn_name": fn_name,
        "input_name": input_name,
        "output_name": output_name,
        "task_id": task_variant.task_id,
        "schema_id": task_variant.task_schema_id,
        "version": version,
    }

    run_code = _run_code_block(input_str, **template_args)
    stream_code = _stream_code_block(input_str, **template_args)

    imports.append(Import.from_full_path("workflowai"))
    imports.append(Import.from_full_path("workflowai.Run"))
    imports.append(Import.from_full_path("workflowai.WorkflowAIError"))

    if url:
        imports.append(Import.from_full_path("os"))

    # Dumping here to add additional imports
    run = CodeWithImports(imports.dump(), run_code)

    imports.append(Import.from_full_path("collections.abc.AsyncIterator"))

    return RunCode(
        common=f"""{_init_code(url)}


{io_code}""",
        run=run,
        stream=CodeWithImports(imports.dump(), stream_code),
    )
