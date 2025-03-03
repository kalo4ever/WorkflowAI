from core.domain.task_group import TaskGroup
from core.domain.task_group_properties import TaskGroupProperties


def test_task_run_group_default_tags() -> None:
    group = TaskGroup(
        properties=TaskGroupProperties(model="gemini-1.5-pro-preview-0409", temperature=0),
    )
    assert group.tags == ["model=gemini-1.5-pro-preview-0409", "temperature=0"]


def test_task_run_group_schema() -> None:
    schema = TaskGroup.model_json_schema()
    assert set(schema["required"]) == {"id", "iteration", "properties", "tags", "similarity_hash"}


def test_task_group_is_favorite():
    # Test when is_favorite is explicitly set to True
    group_favorite = TaskGroup(id="1", iteration=1, properties=TaskGroupProperties(), tags=["test"], is_favorite=True)
    assert group_favorite.is_favorite is True

    # Test when is_favorite is explicitly set to False
    group_not_favorite = TaskGroup(
        id="2",
        iteration=2,
        properties=TaskGroupProperties(),
        tags=["test"],
        is_favorite=False,
    )
    assert group_not_favorite.is_favorite is False

    # Test default behavior (is_favorite should be None)
    group_default = TaskGroup(id="3", iteration=3, properties=TaskGroupProperties(), tags=["test"])
    assert group_default.is_favorite is None


def test_task_group_schema_includes_is_favorite():
    schema = TaskGroup.model_json_schema()
    assert "is_favorite" in schema["properties"]
    assert schema["properties"]["is_favorite"].get("anyOf") == [{"type": "boolean"}, {"type": "null"}]
    assert schema["properties"]["is_favorite"]["default"] is None
    assert "Indicates if the task group is marked as favorite" in schema["properties"]["is_favorite"]["description"]


def test_task_group_notes():
    # Test when notes is set
    group_with_notes = TaskGroup(
        id="1",
        iteration=1,
        properties=TaskGroupProperties(),
        tags=["test"],
        notes="Some notes",
    )
    assert group_with_notes.notes == "Some notes"

    # Test when notes is not set (should be None)
    group_without_notes = TaskGroup(id="2", iteration=2, properties=TaskGroupProperties(), tags=["test"])
    assert group_without_notes.notes is None
