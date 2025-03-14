from pydantic import BaseModel


class RunIdentifier(BaseModel):
    tenant: str
    task_id: str
    task_schema_id: int
    run_id: str
