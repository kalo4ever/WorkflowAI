import asyncio
import os

from azure.core.exceptions import ResourceExistsError
from azure.core.pipeline.transport import AioHttpTransport
from azure.storage.blob import PublicAccess
from azure.storage.blob.aio import BlobServiceClient
from dotenv import load_dotenv

# Make a blob public


async def main(connection_string: str, container_name: str):
    async with BlobServiceClient.from_connection_string(
        connection_string,
        transport=AioHttpTransport(),
    ) as blob_service_client:
        clt = blob_service_client.get_container_client(container_name)

        try:
            clt = await blob_service_client.create_container(container_name)
        except ResourceExistsError:
            pass

        await clt.set_container_access_policy(  # type: ignore
            signed_identifiers={},
            public_access=PublicAccess.BLOB,
        )


if __name__ == "__main__":
    load_dotenv(override=True)

    connection_string = os.environ["WORKFLOWAI_STORAGE_CONNECTION_STRING"]
    if "http://127.0.0.1:10000/devstoreaccount1" not in connection_string:
        print("This script is only supported for local development storage")
        os.abort()

    container_name = os.environ["WORKFLOWAI_STORAGE_TASK_RUNS_CONTAINER"]

    asyncio.run(main(connection_string, container_name))
