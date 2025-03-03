from typing import Annotated

from fastapi import Depends, HTTPException

from api.dependencies.storage import StorageDep
from core.domain.task_variant import SerializableTaskVariant
from core.storage import ObjectNotFoundException


async def latest_task_variant_id(task_id: str, task_schema_id: int, storage: StorageDep) -> SerializableTaskVariant:
    # TODO: return task schema when we have removed task variants
    try:
        return await storage.task_variant_latest_by_schema_id(task_id, task_schema_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Task variant not found")


TaskVariantDep = Annotated[SerializableTaskVariant, Depends(latest_task_variant_id)]
