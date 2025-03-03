from httpx import AsyncClient
from pytest_httpx import HTTPXMock
from taskiq import InMemoryBroker

from core.domain.models import Model
from tests.integration.common import (
    IntegrationTestClient,
    create_task,
    fetch_run,
    mock_openai_call,
    mock_vertex_call,
    result_or_raise,
    run_task,
    run_task_v1,
    wait_for_completed_tasks,
)


# Tests old behavior -> config id is used if possible when a deployment does not exist
# TODO: we likely want to remove this behavior when we fully use deployments
async def test_run_with_custom_provider(
    httpx_mock: HTTPXMock,
    int_api_client: AsyncClient,
    patched_broker: InMemoryBroker,
):
    mock_openai_call(
        httpx_mock,
        usage={"prompt_tokens": 1000000, "completion_tokens": 1000000, "total_tokens": 2000000},
    )
    mock_openai_call(
        httpx_mock,
        provider="azure_openai",
        usage={"prompt_tokens": 1000000, "completion_tokens": 1000000, "total_tokens": 2000000},
    )
    # Check that we do not decrement credits for runs with custom providers
    task = await create_task(int_api_client, patched_broker, httpx_mock)

    # Fetch the organization settings before running the task
    org = result_or_raise(await int_api_client.get("/_/organization/settings"))
    assert org["current_credits_usd"] == 10.0

    # Create a custom provider
    result_or_raise(
        await int_api_client.post(
            "/_/organization/settings/providers",
            json={
                "provider": "azure_openai",
                "deployments": {
                    "eastus": {
                        "api_key": "custom_api_key",
                        "url": "https://workflowai-azure-oai-staging-eastus.openai.azure.com/openai/deployments/",
                        "models": ["gpt-4o-2024-11-20"],
                    },
                },
            },
        ),
    )

    org = result_or_raise(await int_api_client.get("/_/organization/settings"))
    assert org["providers"] and len(org["providers"]) == 1

    # Now run the task
    # run = await run_task(int_api_client, task_id=task["task_id"], task_schema_id=task["task_schema_id"])
    # await wait_for_completed_tasks(patched_broker)
    # fetched_run = await fetch_run(int_api_client, task, run)
    # assert fetched_run["config_id"] == org["providers"][0]["id"]
    # assert org["current_credits_usd"] == 10.0

    # org = result_or_raise(await int_api_client.get("/_/organization/settings"))

    # Now mock with a different provider
    mock_vertex_call(httpx_mock, model="gemini-1.5-pro-001")
    run2 = await run_task(
        int_api_client,
        task_id=task["task_id"],
        task_schema_id=task["task_schema_id"],
        model="gemini-1.5-pro-001",
    )
    await wait_for_completed_tasks(patched_broker)
    fetched_run2 = await fetch_run(int_api_client, task, run2)
    assert not fetched_run2.get("config_id")

    await wait_for_completed_tasks(patched_broker)

    org = result_or_raise(await int_api_client.get("/_/organization/settings"))
    assert org["current_credits_usd"] < 10.0


async def test_run_with_custom_provider_v1(test_client: IntegrationTestClient):
    # Check that we do not decrement credits for runs with custom providers
    task = await test_client.create_task()

    # Fetch the organization settings before running the task
    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))
    assert org["current_credits_usd"] == 10.0

    test_client.mock_openai_call(
        provider="azure_openai",
        usage={"prompt_tokens": 10000, "completion_tokens": 10000, "total_tokens": 200000},
    )
    # Create a custom provider
    result_or_raise(
        await test_client.int_api_client.post(
            "/_/organization/settings/providers",
            json={
                "provider": "azure_openai",
                "deployments": {
                    "eastus": {
                        "api_key": "custom_api_key",
                        "url": "https://workflowai-azure-oai-staging-eastus.openai.azure.com/openai/deployments/",
                        "models": ["gpt-4o-2024-11-20"],
                    },
                },
            },
        ),
    )

    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))
    assert org["providers"] and len(org["providers"]) == 1

    test_client.mock_openai_call(
        usage={"prompt_tokens": 10000, "completion_tokens": 10000, "total_tokens": 200000},
    )
    # Now run the task
    run = await test_client.run_task_v1(task, model=Model.GPT_4O_2024_11_20)
    await test_client.wait_for_completed_tasks()

    # Customer key is not used by default, we need to create a deployment to use it
    fetched_run = await fetch_run(test_client.int_api_client, task, run)
    assert not fetched_run.get("config_id")
    # Credits were removed
    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))
    assert org["current_credits_usd"] == 10.0 - 0.000_002_5 * 10000 - 0.000_010 * 10000

    # Now deploy the task
    res = result_or_raise(
        await test_client.int_api_client.post(
            f"/_/agents/{task['task_id']}/schemas/{task['task_schema_id']}/versions/{fetched_run['group']['iteration']}/deploy",
            json={"environment": "dev", "provider_config_id": org["providers"][0]["id"]},
        ),
    )
    run = await test_client.run_task_v1(task, version="dev", use_cache="never")
    await test_client.wait_for_completed_tasks()
    fetched_run = await fetch_run(test_client.int_api_client, task, run)
    assert fetched_run["config_id"] == org["providers"][0]["id"]
    # Credits were not removed
    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))
    assert org["current_credits_usd"] == 10.0 - 0.000_002_5 * 10000 - 0.000_010 * 10000

    assert res["provider_config_id"] == org["providers"][0]["id"]

    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))

    # Now mock with a different provider
    test_client.mock_vertex_call(model="gemini-1.5-pro-001")
    run2 = await test_client.run_task_v1(task, model="gemini-1.5-pro-001")
    await test_client.wait_for_completed_tasks()
    fetched_run2 = await fetch_run(test_client.int_api_client, task, run2)
    assert not fetched_run2.get("config_id")

    await test_client.wait_for_completed_tasks()

    org = result_or_raise(await test_client.int_api_client.get("/_/organization/settings"))
    assert org["current_credits_usd"] < 10.0


async def test_run_with_custom_provider_and_config_id(
    httpx_mock: HTTPXMock,
    int_api_client: AsyncClient,
    patched_broker: InMemoryBroker,
):
    mock_openai_call(
        httpx_mock,
        provider="azure_openai",
        usage={"prompt_tokens": 1000000, "completion_tokens": 1000000, "total_tokens": 2000000},
    )
    # Check that we do not decrement credits for runs with custom providers
    task = await create_task(int_api_client, patched_broker, httpx_mock)

    # Fetch the organization settings before running the task
    org = result_or_raise(await int_api_client.get("/_/organization/settings"))
    assert org["current_credits_usd"] == 10.0

    # Create a custom provider
    result_or_raise(
        await int_api_client.post(
            "/_/organization/settings/providers",
            json={
                "provider": "azure_openai",
                "deployments": {
                    "eastus": {
                        "api_key": "custom_api_key",
                        "url": "https://workflowai-azure-oai-staging-eastus.openai.azure.com/openai/deployments/",
                        "models": ["gpt-4o-2024-11-20"],
                    },
                },
            },
        ),
    )
    org = result_or_raise(await int_api_client.get("/_/organization/settings"))
    assert org["providers"] and len(org["providers"]) == 1

    # Create a group with a custom provider
    group = result_or_raise(
        await int_api_client.post(
            f"/_/agents/{task['task_id']}/schemas/{task['task_schema_id']}/groups",
            json={"properties": {"model": "gpt-4o-2024-11-20", "provider": "openai"}},
        ),
    )

    # Deploy the group and add the provider config id
    res = result_or_raise(
        await int_api_client.post(
            f"/_/agents/{task['task_id']}/schemas/{task['task_schema_id']}/versions/{group['iteration']}/deploy",
            json={
                "environment": "dev",
                "provider_config_id": org["providers"][0]["id"],
            },
        ),
    )
    assert res["provider_config_id"] == org["providers"][0]["id"]
    # Now run the task
    run = await run_task_v1(
        int_api_client,
        task_id=task["task_id"],
        task_schema_id=task["task_schema_id"],
        version="dev",
    )
    await wait_for_completed_tasks(patched_broker)
    fetched_run = await fetch_run(int_api_client, task, run)
    assert fetched_run["config_id"] == org["providers"][0]["id"]

    org = result_or_raise(await int_api_client.get("/_/organization/settings"))
    assert org["current_credits_usd"] == 10.0

    # Now mock with a different provider
    mock_vertex_call(httpx_mock, model="gemini-1.5-pro-001")
    run2 = await run_task_v1(
        int_api_client,
        task_id=task["task_id"],
        task_schema_id=task["task_schema_id"],
        model="gemini-1.5-pro-001",
    )
    await wait_for_completed_tasks(patched_broker)
    fetched_run2 = await fetch_run(int_api_client, task, run2)
    assert not fetched_run2.get("config_id")

    await wait_for_completed_tasks(patched_broker)

    org = result_or_raise(await int_api_client.get("/_/organization/settings"))
    assert org["current_credits_usd"] < 10.0
