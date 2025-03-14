from fastapi import APIRouter, UploadFile
from pydantic import BaseModel

from api.dependencies.security import TenantDep
from api.dependencies.services import FileStorageDep
from core.domain.fields.file import DomainUploadFile

router = APIRouter(prefix="/upload")


class UploadFileResponse(BaseModel):
    url: str


@router.post("/{task_id}", response_model=UploadFileResponse)
async def upload_file(
    file_storage: FileStorageDep,
    tenant: TenantDep,
    task_id: str,
    file: UploadFile,
) -> UploadFileResponse:
    url = await file_storage.store_file(
        DomainUploadFile(
            filename=file.filename or "",
            contents=await file.read(),
            content_type=file.content_type or "",
        ),
        f"{tenant}/{task_id}/uploads",
    )
    return UploadFileResponse(url=url)
