from core.storage.mongo.models.pyobjectid import PyObjectID

from .task_example import TaskExampleDocument
from .task_metadata import TaskMetadataSchema


def test_example_to_resource() -> None:
    example = TaskExampleDocument(
        _id=PyObjectID.from_str("65f4cb8b099fee6ccf2f064f"),
        task=TaskMetadataSchema(
            id="1",
            schema_id=1,
        ),
        tenant="tenant",
        task_input_hash="4",
        task_input={},
        task_input_preview="input",
        task_output={},
        task_output_hash="5",
        task_output_preview="5",
    )

    resource = example.to_resource()
    assert resource.id == "65f4cb8b099fee6ccf2f064f"
    assert resource.created_at is not None
    assert resource.created_at.isoformat() == "2024-03-15T22:28:27+00:00"
