import logging
from datetime import datetime
from typing import Self

from fastapi import APIRouter
from pydantic import BaseModel

from core.domain.task_run_aggregate_per_day import TaskRunAggregatePerDay
from core.domain.task_run_query import SerializableTaskRunQuery

from ..dependencies.storage import StorageDep

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/runs/stats")


class TaskStats(BaseModel):
    total_count: int
    total_cost_usd: float
    date: str

    @classmethod
    def from_domain(cls, item: TaskRunAggregatePerDay) -> Self:
        return cls(
            total_count=item.total_count,
            total_cost_usd=item.total_cost_usd,
            date=item.date.isoformat(),
        )


class TaskStatsResponse(BaseModel):
    data: list[TaskStats]


@router.get("")
async def get_tenant_stats(
    storage: StorageDep,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    is_active: bool | None = None,
) -> TaskStatsResponse:
    query = SerializableTaskRunQuery(
        task_id=None,
        task_schema_id=None,
        created_after=created_after,
        created_before=created_before,
        is_active=is_active,
    )
    data: list[TaskStats] = []
    async for item in storage.task_runs.aggregate_task_run_costs(None, query):
        task_stat = TaskStats.from_domain(item)
        data.append(task_stat)
    return TaskStatsResponse(data=data)
