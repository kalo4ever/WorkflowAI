import asyncio
import os
from typing import Any, Protocol, TypedDict

import httpx
import pytest
from dotenv import load_dotenv

load_dotenv(override=True)


class VersionProperties(TypedDict):
    model: str
    provider: str
    extra_items: dict[str, str]


class Version(TypedDict):
    properties: VersionProperties


class RunOutput(TypedDict):
    id: str
    task_output: dict[str, Any]
    duration_seconds: float
    cost_usd: float
    version: Version


@pytest.fixture(scope="module")
def e2e_tenant() -> str:
    if tenant := os.environ.get("TEST_E2E_TENANT"):
        return tenant
    pytest.skip("TEST_E2E_TENANT is not set")


@pytest.fixture(scope="module")
def e2e_api_url() -> str:
    if url := os.environ.get("TEST_E2E_API_URL"):
        return url
    pytest.skip("TEST_E2E_API_URL is not set")


@pytest.fixture(scope="module")
def e2e_api_token() -> str:
    if token := os.environ.get("TEST_E2E_API_TOKEN"):
        return token
    pytest.skip("TEST_E2E_API_TOKEN is not set")


class ApiRunFn(Protocol):
    async def __call__(
        self,
        task_id: str,
        schema_id: int,
        input: dict[str, Any],
        version: str | int | dict[str, Any],
        assert_model: str | None = None,
        max_allowed_duration_seconds: float = 30,
        use_cache: bool = False,
    ) -> RunOutput: ...


@pytest.fixture(scope="module")
def run_fn(e2e_api_url: str, e2e_tenant: str, e2e_api_token: str) -> ApiRunFn:
    async def _run_task(
        task_id: str,
        schema_id: int,
        input: dict[str, Any],
        version: str | int | dict[str, Any],
        assert_model: str | None = None,
        max_allowed_duration_seconds: float = 30,
        use_cache: bool = False,
    ) -> RunOutput:
        async with asyncio.timeout(max_allowed_duration_seconds):
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{e2e_api_url}/v1/{e2e_tenant}/agents/{task_id}/schemas/{schema_id}/run",
                    headers={"Authorization": f"Bearer {e2e_api_token}"},
                    json={
                        "task_input": input,
                        "version": version,
                        "use_cache": "auto" if use_cache else "never",
                    },
                    timeout=120,
                )
                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError as e:
                    print(f"Status code: {response.status_code}")  # noqa: T201
                    print(f"Response text: {response.text}")  # noqa: T201
                    raise e

                responded: RunOutput = response.json()

        if assert_model:
            assert responded["version"]["properties"]["model"] == assert_model

        return responded

    return _run_task
