import base64
import logging
from typing import Protocol

from azure.core.exceptions import ResourceExistsError
from azure.core.pipeline.transport import AioHttpTransport
from azure.storage.blob.aio import BlobClient, BlobServiceClient

from core.domain.fields.file import DomainUploadFile, File


class FileStorage(Protocol):
    async def store_file(self, file: File | DomainUploadFile, folder_path: str) -> str: ...


class CouldNotStoreFileError(Exception):
    pass


class AzureBlobFileStorage:
    def __init__(self, connection_string: str, container_name: str):
        self.connection_string = connection_string
        self.container_name = container_name

        self._logger = logging.getLogger(__name__)

    async def _get_blob_service_client(self) -> BlobServiceClient:
        return BlobServiceClient.from_connection_string(
            self.connection_string,
            # TODO: refine these settings after monitoring performance
            transport=AioHttpTransport(
                connection_timeout=300.0,
                read_timeout=300.0,
                retries=3,
                maximum_valid_request_size=500 * 1024 * 1024,
            ),
        )

    async def store_file(self, file: File | DomainUploadFile, folder_path: str) -> str:
        # folder_path is like /{tenant}/{task_id}

        if isinstance(file, DomainUploadFile):
            contents = file.contents
        elif file.data:
            contents = base64.b64decode(file.data)
        else:
            raise ValueError("File contents cannot be None")

        content_hash = file.get_content_hash()
        extension = file.get_extension()
        blob_name = f"{folder_path}/{content_hash}{extension}"

        async with await self._get_blob_service_client() as blob_service_client:
            try:
                blob_client: BlobClient = blob_service_client.get_blob_client(
                    container=self.container_name,
                    blob=blob_name,
                )
                # TODO: Update or add parameters to upload_blob based on performance.
                # It supports chunking, compression, concurrency, and encryption
                try:
                    await blob_client.upload_blob(
                        contents,
                        content_type=file.content_type,
                        overwrite=False,
                    )
                    return blob_client.url  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
                except ResourceExistsError:
                    # If the file already exists, we don't need to do anything
                    return blob_client.url  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            except Exception as e:
                raise CouldNotStoreFileError() from e
