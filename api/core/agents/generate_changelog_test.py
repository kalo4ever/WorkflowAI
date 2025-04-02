from .generate_changelog import (
    GenerateChangelogFromPropertiesTaskInput,
    Properties,
    Schema,
    TaskGroupWithSchema,
)


class TestGenerateChangelogFromPropertiesTaskInput:
    def test_dump_by_alias(self):
        old_task_group = TaskGroupWithSchema(
            properties=Properties(instructions="", temperature=0.0, few_shot=False),
            schema=Schema(input_json_schema="hello", output_json_schema="world"),
        )
        task_input = GenerateChangelogFromPropertiesTaskInput(
            old_task_group=old_task_group,
            new_task_group=old_task_group,
        )

        assert task_input.model_dump() == {
            "old_task_group": {
                "properties": {"instructions": "", "temperature": 0.0, "few_shot": False},
                "schema": {"input_json_schema": "hello", "output_json_schema": "world"},
            },
            "new_task_group": {
                "properties": {"instructions": "", "temperature": 0.0, "few_shot": False},
                "schema": {"input_json_schema": "hello", "output_json_schema": "world"},
            },
        }
