from core.storage.mongo.models.base_document import BaseDocument


class TaskGroupIterations(BaseDocument):
    """A document to allow having auto incremented iterations for task run groups"""

    task_id: str

    latest_iteration: int
