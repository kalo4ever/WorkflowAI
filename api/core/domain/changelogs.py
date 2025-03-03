from pydantic import BaseModel

from api.dependencies.path_params import TaskID, TaskSchemaID


class VersionChangelog(BaseModel):
    task_id: TaskID
    task_schema_id: TaskSchemaID

    major_from: int
    major_to: int
    similarity_hash_from: str
    similarity_hash_to: str

    changelog: list[str]
