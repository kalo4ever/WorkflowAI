import base64
import os
from io import FileIO

import pytest

from core.domain.fields.file import DomainUploadFile, File
from core.storage.azure.azure_blob_file_storage import AzureBlobFileStorage
from tests.utils import fixture_bytes, fixture_path


@pytest.fixture
async def azure_blob_storage(
    # Using global fixture to make sure the container is created
    test_blob_storage: None,
) -> AzureBlobFileStorage:
    return AzureBlobFileStorage(
        connection_string=os.environ["WORKFLOWAI_STORAGE_CONNECTION_STRING"],
        container_name=os.environ["WORKFLOWAI_STORAGE_TASK_RUNS_CONTAINER"],
    )


async def test_connection_established(azure_blob_storage: AzureBlobFileStorage):
    # Test that we can establish a connection and get container client
    blob_service_client = await azure_blob_storage._get_blob_service_client()  # pyright: ignore[reportPrivateUsage]
    assert blob_service_client is not None

    # Test that we can get a blob client
    blob_client_properties = await blob_service_client.get_service_properties()
    assert blob_client_properties is not None

    container_properties = await blob_service_client.get_container_client(
        azure_blob_storage.container_name,
    ).get_container_properties()
    assert container_properties is not None


async def test_store_file(azure_blob_storage: AzureBlobFileStorage):
    blob_service_client = await azure_blob_storage._get_blob_service_client()  # pyright: ignore[reportPrivateUsage]
    assert blob_service_client is not None
    assert hasattr(blob_service_client, "url")

    file_data = fixture_bytes("files", "test.png")
    base64_data = base64.b64encode(file_data).decode("utf-8")
    file = File(content_type="image/png", data=base64_data)

    folder_path = "test/local"
    content_hash = file.get_content_hash()
    blob_name = f"{folder_path}/{content_hash}.png"
    url = await azure_blob_storage.store_file(file, folder_path)

    container_url = f"{blob_service_client.url}{azure_blob_storage.container_name}"  # type: ignore
    assert url == f"{container_url}/{blob_name}"


async def test_store_upload_file(azure_blob_storage: AzureBlobFileStorage):
    blob_service_client = await azure_blob_storage._get_blob_service_client()  # pyright: ignore[reportPrivateUsage]
    assert blob_service_client is not None
    assert hasattr(blob_service_client, "url")

    _file = FileIO(file=fixture_path("files", "test.png"))
    file = DomainUploadFile(
        filename="test.png",
        contents=_file.read(),
        content_type="image/png",
    )
    folder_path = "test/local"
    content_hash = file.get_content_hash()
    blob_name = f"{folder_path}/{content_hash}.png"
    url = await azure_blob_storage.store_file(file, folder_path)

    container_url = f"{blob_service_client.url}{azure_blob_storage.container_name}"  # type: ignore
    assert url == f"{container_url}/{blob_name}"
