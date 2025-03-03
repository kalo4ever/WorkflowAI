import pytest

from core.domain.task_group import TaskGroup
from core.domain.task_group_properties import TaskGroupProperties
from core.domain.task_io import SerializableTaskIO
from core.domain.task_run import SerializableTaskRun
from core.domain.task_variant import SerializableTaskVariant


@pytest.fixture(scope="function")
def task_run_resource() -> SerializableTaskRun:
    return SerializableTaskRun(
        id="run_id",
        task_id="task_id",
        task_schema_id=1,
        task_input={"input": "world"},
        task_input_hash="input_hash",
        task_output={
            "output": 1,
        },
        task_output_hash="output_hash",
        group=TaskGroup(
            id="group_id",
            iteration=1,
            properties=TaskGroupProperties.model_construct(model="model"),
            tags=["tag"],
        ),
    )


@pytest.fixture(scope="function")
def task_version_resource() -> SerializableTaskVariant:
    return SerializableTaskVariant(
        id="task_version_id",
        task_id="task_id",
        name="task_name",
        task_schema_id=1,
        input_schema=SerializableTaskIO(
            version="input_version",
            json_schema={"type": "object", "properties": {"input": {"type": "string"}}, "required": ["input"]},
        ),
        output_schema=SerializableTaskIO(
            version="output_version",
            json_schema={"type": "object", "properties": {"output": {"type": "integer"}}, "required": ["output"]},
        ),
    )
