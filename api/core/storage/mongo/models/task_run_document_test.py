from core.storage.mongo.models.task_run_document import TaskRunDocument
from tests import models


def test_resource_conversion_sanity() -> None:
    task_run_resource = models.task_run_ser()

    schema = TaskRunDocument.from_resource(task_run_resource)
    converted = schema.to_resource()

    assert task_run_resource == converted
