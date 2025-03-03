from unittest.mock import Mock

import pytest
from httpx import AsyncClient

from core.providers.base import httpx_provider
from core.providers.base.client_pool import ClientPool


@pytest.fixture(autouse=True)
async def patched_client_pool():
    current = httpx_provider.shared_client_pool
    httpx_provider.shared_client_pool = Mock(spec=ClientPool)
    client = AsyncClient()
    httpx_provider.shared_client_pool.get.return_value = client
    yield
    await client.aclose()
    httpx_provider.shared_client_pool = current
