from core.agents.task_input_example.task_input_example_task import TaskInputExampleTaskInput


class TestInputLabel:
    def test_input_label_equals(self):
        input1 = TaskInputExampleTaskInput(
            current_datetime="2024-01-01T00:00:00Z",
            task_name="test_task",
            input_json_schema={"type": "object", "properties": {"name": {"type": "string"}}},
            output_json_schema={"type": "object", "properties": {"name": {"type": "string"}}},
            additional_instructions="Add a name property",
        )

        input2 = input1.model_copy(update={"current_datetime": "2024-01-03T00:00:00Z"})
        input3 = input1.model_copy(update={"previous_task_inputs": {"h": "1"}})

        expected = input1.memory_id()
        assert expected == input2.memory_id()
        assert expected == input3.memory_id()

    def test_input_label_not_equals(self):
        input1 = TaskInputExampleTaskInput(
            current_datetime="2024-01-01T00:00:00Z",
            task_name="test_task",
            input_json_schema={"type": "object", "properties": {"name": {"type": "string"}}},
            output_json_schema={"type": "object", "properties": {"name": {"type": "string"}}},
            additional_instructions="Add a name property",
        )

        input2 = input1.model_copy(update={"task_name": "bla"})
        assert input1.memory_id() != input2.memory_id()

        input3 = input1.model_copy(update={"additional_instructions": "Add another name property "})
        assert input1.memory_id() != input3.memory_id()
