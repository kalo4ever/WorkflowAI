import os

from fastapi import APIRouter, HTTPException, Response

from api.dependencies.encryption import EncryptionDep
from api.dependencies.security import KeyRingDep
from api.services import storage
from core.utils import no_op

router = APIRouter(prefix="/probes", include_in_schema=False)


async def is_storage_ready(encryption: EncryptionDep):
    s = storage.storage_for_tenant("", -1, no_op.event_router, encryption)
    return await s.is_ready()


IGNORE_STORAGE_IN_PROBES = os.getenv("IGNORE_STORAGE_IN_PROBES") == "true"


async def check_storage_ready(encryption: EncryptionDep):
    if await is_storage_ready(encryption):
        return
    if not IGNORE_STORAGE_IN_PROBES:
        raise HTTPException(status_code=503, detail="Storage is not ready")


@router.get("/readiness")
async def readiness(
    encryption: EncryptionDep,
    keys: KeyRingDep,
) -> Response:
    # Load all possible dependencies and return ok when good
    await check_storage_ready(encryption)
    return Response(status_code=200)


class HealthErrorCounter:
    def __init__(self):
        self.error_count = 0

    def increment(self):
        self.error_count += 1

    def get(self):
        return self.error_count

    def reset(self):
        self.error_count = 0


error_counter = HealthErrorCounter()


@router.head("/health")
async def health_head() -> Response:
    # Head endpoint will be called by the front door profile
    # which means it will be called a lot
    # see https://learn.microsoft.com/en-us/azure/frontdoor/health-probes
    # So we remove the actual db check and check the database asynchronously
    # since the health get endpoint will be called a lot less frequently
    # by the container app health checks
    if error_counter.get() > 2:
        return Response(status_code=503)
    return Response(status_code=200)


@router.get("/health")
async def health(
    encryption: EncryptionDep,
    keys: KeyRingDep,
) -> Response:
    # Load all possible dependencies and return ok when good
    try:
        await check_storage_ready(encryption)
        error_counter.reset()
        return Response(status_code=200)
    except Exception as e:
        error_counter.increment()
        raise e
