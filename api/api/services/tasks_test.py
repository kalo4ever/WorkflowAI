import glob
import os
import re
from unittest.mock import AsyncMock, Mock

from core.domain.task import SerializableTask
from core.domain.task_info import TaskInfo

from .tasks import INTERNAL_TASK_IDS, AgentSummary, list_agent_summaries, list_tasks


class TestListTasks:
    def test_internal_exhaustive(self):
        internal_tasks_dir = os.path.join(os.path.dirname(__file__), "..", "..", "core", "tasks")
        task_files = glob.glob("**/*task.py", root_dir=internal_tasks_dir, recursive=True)
        pattern = re.compile(r"([a-zA-Z0-9]+)Task\(")

        task_ids = set[str]()

        for file_path in task_files:
            with open(os.path.join(internal_tasks_dir, file_path), "r") as file:
                for line in file:
                    matches = pattern.findall(line)

                    if not matches:
                        continue

                    task_id = matches[0].lower()
                    assert task_id not in task_ids, f"Duplicate task id: {task_id}"
                    task_ids.add(task_id)
                    break

        assert task_ids.issubset(INTERNAL_TASK_IDS)

    async def test_list_tasks(self, mock_storage: Mock):
        mock_iter = AsyncMock()

        mock_iter.__aiter__.return_value = [
            SerializableTask(
                id="task1",
                name="Task 1",
                versions=[
                    SerializableTask.PartialTaskVersion(
                        schema_id=1,
                        variant_id="variant1",
                        input_schema_version="input1",
                        output_schema_version="output1",
                    ),
                    SerializableTask.PartialTaskVersion(
                        schema_id=1,
                        variant_id="variant2",
                        input_schema_version="input1",
                        output_schema_version="output1",
                    ),
                    SerializableTask.PartialTaskVersion(
                        schema_id=2,
                        variant_id="variant1",
                        input_schema_version="input1",
                        output_schema_version="output1",
                    ),
                ],
            ),
            SerializableTask(
                id="generateevaluationinstructions",
                name="Internal task 1",
                versions=[
                    SerializableTask.PartialTaskVersion(
                        schema_id=1,
                        variant_id="variant1",
                        input_schema_version="input1",
                        output_schema_version="output1",
                    ),
                ],
            ),
        ]

        mock_storage.fetch_tasks.return_value = mock_iter
        mock_storage.tasks.get_task_info.return_value = TaskInfo(
            task_id="task1",
            name="Task 1",
            description="Test task description",
            is_public=False,
            hidden_schema_ids=[],
        )

        tasks = await list_tasks(mock_storage)
        assert tasks == [
            SerializableTask(
                id="task1",
                name="Task 1",
                description="Test task description",
                is_public=False,
                tenant="",
                versions=[
                    SerializableTask.PartialTaskVersion(
                        schema_id=1,
                        variant_id="variant1",
                        input_schema_version="input1",
                        output_schema_version="output1",
                        is_hidden=False,
                    ),
                    SerializableTask.PartialTaskVersion(
                        schema_id=2,
                        variant_id="variant1",
                        input_schema_version="input1",
                        output_schema_version="output1",
                        is_hidden=False,
                    ),
                ],
            ),
        ]

    async def test_list_agent_summaries(self, mock_storage: Mock) -> None:
        mock_iter: AsyncMock = AsyncMock()
        # Provide tasks in unsorted order to test ordering of agents by name.
        mock_iter.__aiter__.return_value = [
            SerializableTask(
                id="task2",
                name="Task 2",
                description="Description 2",
                versions=[],
            ),
            SerializableTask(
                id="task1",
                name="Task 1",
                description="Description 1",
                versions=[],
            ),
        ]

        mock_storage.fetch_tasks.return_value = mock_iter

        summaries = await list_agent_summaries(mock_storage)
        # Expected summaries should be returned in ascending order of agent names.
        assert summaries == [
            AgentSummary(name="Task 1", description="Description 1"),
            AgentSummary(name="Task 2", description="Description 2"),
        ]


class TestAgentSummary:
    def test_agent_summary_with_description(self):
        summary = AgentSummary(name="Test Agent", description="Test Description")
        assert str(summary) == "Test Agent: Test Description"

    def test_agent_summary_without_description(self):
        summary = AgentSummary(name="Test Agent", description=None)
        assert str(summary) == "Test Agent"
