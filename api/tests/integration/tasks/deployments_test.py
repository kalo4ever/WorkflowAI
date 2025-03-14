import pytest
from httpx import AsyncClient
from pytest_httpx import HTTPXMock
from taskiq import InMemoryBroker

from tests.integration.common import (
    IntegrationTestClient,
    create_task,
    create_version,
    openai_endpoint,
    result_or_raise,
    wait_for_completed_tasks,
)
from tests.utils import request_json_body


async def test_deploy_version_not_found(
    int_api_client: AsyncClient,
    httpx_mock: HTTPXMock,
    patched_broker: InMemoryBroker,
):
    task = await create_task(int_api_client, patched_broker, httpx_mock)
    res = await int_api_client.post(
        f"/chiefofstaff.ai/agents/{task['task_id']}/schemas/{task['task_schema_id']}/versions/1/deploy",
        json={"environment": "production", "provider_config_id": "config1"},
    )
    assert res.status_code == 404


async def test_deploy_one_version_one_environment(
    int_api_client: AsyncClient,
    httpx_mock: HTTPXMock,
    patched_broker: InMemoryBroker,
):
    task = await create_task(int_api_client, patched_broker, httpx_mock)
    assert task["task_id"] == "greet"
    assert task["task_schema_id"] == 1

    version = await create_version(
        int_api_client,
        task_id="greet",
        task_schema_id=1,
        version_properties={"instructions": "some instructions", "model": "gemini-1.5-pro-002"},
    )
    assert version["iteration"] == 1
    res = await int_api_client.post(
        "/chiefofstaff.ai/agents/greet/schemas/1/versions/1/deploy",
        json={
            "environment": "production",
            "provider_config_id": "config1",
        },
    )
    assert res.status_code == 200
    deployment = res.json()

    assert deployment["version_id"] == 1
    assert deployment["task_schema_id"] == task["task_schema_id"]
    assert deployment["environment"] == "production"
    assert deployment["provider_config_id"] == "config1"
    assert "deployed_at" in deployment

    await wait_for_completed_tasks(patched_broker)


@pytest.mark.parametrize(
    "environment, config_id1, config_id2",
    [
        ("dev", "config1", ""),
        ("staging", "", "config2"),
        ("production", "config1", "config2"),
        ("production", None, "conf1"),
        ("dev", "config1", None),
    ],
)
async def test_deploy_version_override(
    environment: str,
    int_api_client: AsyncClient,
    httpx_mock: HTTPXMock,
    patched_broker: InMemoryBroker,
    config_id1: str,
    config_id2: str,
):
    task = await create_task(int_api_client, patched_broker, httpx_mock)
    version = await create_version(
        int_api_client,
        task_id="greet",
        task_schema_id=1,
        version_properties={"instructions": "some instructions", "model": "gemini-1.5-pro-002"},
    )
    assert version["iteration"] == 1
    res = await int_api_client.post(
        f"/chiefofstaff.ai/agents/{task['task_id']}/schemas/{task['task_schema_id']}/versions/1/deploy",
        json={
            "environment": environment,
            "provider_config_id": config_id1,
        },
    )
    first_deployment = result_or_raise(res)
    assert first_deployment["provider_config_id"] == config_id1

    res = await int_api_client.post(
        f"/chiefofstaff.ai/agents/{task['task_id']}/schemas/{task['task_schema_id']}/versions/1/deploy",
        json={
            "environment": environment,
            "provider_config_id": config_id2,
        },
    )
    second_deployment = result_or_raise(res)
    assert second_deployment["provider_config_id"] == config_id2

    res = await int_api_client.get(
        f"/chiefofstaff.ai/agents/{task['task_id']}/versions/deployed",
    )
    deployments = result_or_raise(res)
    assert len(deployments["items"]) == 1
    assert len(deployments["items"][0]["deployments"]) == 1
    assert deployments["items"][0]["deployments"][0]["environment"] == environment
    assert deployments["items"][0]["deployments"][0]["provider_config_id"] == config_id2
    await wait_for_completed_tasks(patched_broker)


@pytest.mark.parametrize(
    "environment",
    ["dev", "staging", "production"],
)
async def test_deploy_version_different_environments(
    environment: str,
    int_api_client: AsyncClient,
    httpx_mock: HTTPXMock,
    patched_broker: InMemoryBroker,
):
    task = await create_task(int_api_client, patched_broker, httpx_mock)

    version = await create_version(
        int_api_client,
        task_id=task["task_id"],
        task_schema_id=task["task_schema_id"],
        version_properties={"instructions": "some instructions", "model": "gemini-1.5-pro-002"},
    )
    res = await int_api_client.post(
        f"/chiefofstaff.ai/agents/{task['task_id']}/schemas/{task['task_schema_id']}/versions/{version['iteration']}/deploy",
        json={
            "environment": environment,
            "provider_config_id": "config1",
        },
    )
    deployment = result_or_raise(res)

    assert deployment["environment"] == environment
    assert deployment["provider_config_id"] == "config1"

    await wait_for_completed_tasks(patched_broker)

    res = await int_api_client.get(
        f"/chiefofstaff.ai/agents/{task['task_id']}/versions/deployed",
    )
    deployments = result_or_raise(res)
    assert len(deployments["items"]) == 1
    assert len(deployments["items"][0]["deployments"]) == 1
    assert deployments["items"][0]["deployments"][0]["environment"] == environment
    assert deployments["items"][0]["deployments"][0]["provider_config_id"] == "config1"
    await wait_for_completed_tasks(patched_broker)


async def test_deploy_version_invalid_environment(
    int_api_client: AsyncClient,
    httpx_mock: HTTPXMock,
    patched_broker: InMemoryBroker,
):
    task = await create_task(int_api_client, patched_broker, httpx_mock)

    res = await int_api_client.post(
        f"/chiefofstaff.ai/agents/{task['task_id']}/schemas/{task['task_schema_id']}/versions/1/deploy",
        json={
            "environment": "invalid",
            "provider_config_id": "config1",
        },
    )
    assert res.status_code == 422  # Validation error


async def test_deploy_to_multiple_environments(
    int_api_client: AsyncClient,
    httpx_mock: HTTPXMock,
    patched_broker: InMemoryBroker,
):
    task = await create_task(int_api_client, patched_broker, httpx_mock)
    version = await create_version(
        int_api_client,
        task_id=task["task_id"],
        task_schema_id=task["task_schema_id"],
        version_properties={"instructions": "some instructions", "model": "gemini-1.5-pro-002"},
    )
    res = await int_api_client.post(
        f"/chiefofstaff.ai/agents/{task['task_id']}/schemas/{task['task_schema_id']}/versions/{version['iteration']}/deploy",
        json={"environment": "dev", "provider_config_id": "config1"},
    )
    deployment = result_or_raise(res)
    assert deployment["environment"] == "dev"
    assert deployment["provider_config_id"] == "config1"

    res = await int_api_client.post(
        f"/chiefofstaff.ai/agents/{task['task_id']}/schemas/{task['task_schema_id']}/versions/{version['iteration']}/deploy",
        json={"environment": "staging", "provider_config_id": "config2"},
    )
    deployment = result_or_raise(res)
    assert deployment["environment"] == "staging"
    assert deployment["provider_config_id"] == "config2"

    await wait_for_completed_tasks(patched_broker)

    res = await int_api_client.get(
        f"/chiefofstaff.ai/agents/{task['task_id']}/versions/deployed",
    )
    deployments = result_or_raise(res)
    assert len(deployments["items"]) == 1
    assert len(deployments["items"][0]["deployments"]) == 2
    assert deployments["items"][0]["deployments"][1]["environment"] == "dev"
    assert deployments["items"][0]["deployments"][1]["provider_config_id"] == "config1"
    assert deployments["items"][0]["deployments"][0]["environment"] == "staging"
    assert deployments["items"][0]["deployments"][0]["provider_config_id"] == "config2"


async def test_deploy_multiple_versions_one_environment_one_schema(
    int_api_client: AsyncClient,
    httpx_mock: HTTPXMock,
    patched_broker: InMemoryBroker,
):
    task = await create_task(int_api_client, patched_broker, httpx_mock)
    version1 = await create_version(
        int_api_client,
        task_id=task["task_id"],
        task_schema_id=task["task_schema_id"],
        version_properties={"instructions": "some instructions", "model": "gemini-1.5-pro-002"},
    )
    version2 = await create_version(
        int_api_client,
        task_id=task["task_id"],
        task_schema_id=task["task_schema_id"],
        version_properties={"instructions": "some instructions 1", "model": "gemini-1.5-pro-001"},
    )

    res = await int_api_client.post(
        f"/chiefofstaff.ai/agents/{task['task_id']}/schemas/{task['task_schema_id']}/versions/{version1['iteration']}/deploy",
        json={"environment": "dev", "provider_config_id": "config1"},
    )
    deployment1 = result_or_raise(res)
    assert deployment1["environment"] == "dev"
    assert deployment1["provider_config_id"] == "config1"

    res = await int_api_client.post(
        f"/chiefofstaff.ai/agents/{task['task_id']}/schemas/{task['task_schema_id']}/versions/{version2['iteration']}/deploy",
        json={"environment": "dev", "provider_config_id": "config2"},
    )
    deployment2 = result_or_raise(res)
    assert deployment2["environment"] == "dev"
    assert deployment2["provider_config_id"] == "config2"

    await wait_for_completed_tasks(patched_broker)

    res = await int_api_client.get(
        f"/chiefofstaff.ai/agents/{task['task_id']}/versions/deployed",
    )
    deployments = result_or_raise(res)
    assert len(deployments["items"]) == 1
    assert len(deployments["items"][0]["deployments"]) == 1
    assert deployments["items"][0]["deployments"][0]["environment"] == "dev"
    assert deployments["items"][0]["deployments"][0]["provider_config_id"] == "config2"
    assert deployments["items"][0]["iteration"] == version2["iteration"]


async def _prepare_deploy_with_config(test_client: IntegrationTestClient):
    # Then create a task
    task = await test_client.create_task()
    # sanity check
    result_or_raise(
        await test_client.int_api_client.get(
            f"/chiefofstaff.ai/agents/{task['task_id']}/schemas/{task['task_schema_id']}",
        ),
    )

    # Create a version
    await test_client.create_version(
        task,
        version_properties={"instructions": "some instructions", "model": "ministral-3b-2410"},
        mock_chain_of_thought=True,
    )
    await test_client.wait_for_completed_tasks()
    test_client.reset_httpx_mock(assert_all_responses_were_requested=True)

    # Run the task
    test_client.mock_mistralai_completion()
    _ = await test_client.run_task_v1(
        task,
        model="ministral-3b-2410",
    )
    test_client.reset_httpx_mock(assert_all_responses_were_requested=True)

    return task


async def test_deploy_provider_config_organization(
    test_client: IntegrationTestClient,
):
    # First, create the provider config for the organization
    # Mock the check we do when creating a provider config
    test_client.mock_mistralai_completion()
    res = await test_client.int_api_client.post(
        "/chiefofstaff.ai/organization/settings/providers",
        json={"provider": "mistral_ai", "api_key": "sk-ant-api03-..."},
    )
    org_settings_id = result_or_raise(res)["id"]
    assert len(test_client.httpx_mock.get_requests(url="https://api.mistral.ai/v1/chat/completions")) == 1
    test_client.reset_httpx_mock()

    task = await _prepare_deploy_with_config(test_client)
    # Deploy
    test_client.mock_mistralai_completion()
    res = await test_client.int_api_client.post(
        f"/chiefofstaff.ai/agents/{task['task_id']}/schemas/{task['task_schema_id']}/versions/1/deploy",
        json={"environment": "dev", "provider_config_id": org_settings_id},
    )
    assert res.status_code == 200
    assert result_or_raise(res)["provider_config_id"] == org_settings_id
    request = test_client.httpx_mock.get_request(url="https://api.mistral.ai/v1/chat/completions")
    assert request
    body = request_json_body(request)
    assert "John" in body["messages"][-1]["content"]
    assert body["messages"][-1]["role"] == "user", "sanity"
    assert body["model"] == "ministral-3b-2410"


async def test_deploy_provider_config_organization_wrong_provider(
    test_client: IntegrationTestClient,
):
    test_client.mock_openai_call(provider="azure_openai")
    res = await test_client.int_api_client.post(
        "/chiefofstaff.ai/organization/settings/providers",
        json={
            "provider": "azure_openai",
            "deployments": {
                "eastus": {
                    "api_key": "sk-ant-api03-...",
                    "url": "https://workflowai-azure-oai-staging-eastus.openai.azure.com/openai/deployments/",
                    "models": ["gpt-4o-2024-11-20"],
                },
            },
        },
    )
    org_settings_id = result_or_raise(res)["id"]
    assert len(test_client.httpx_mock.get_requests(url=openai_endpoint(provider="azure_openai"))) == 1
    test_client.reset_httpx_mock()

    task = await _prepare_deploy_with_config(test_client)

    res = await test_client.int_api_client.post(
        f"/chiefofstaff.ai/agents/{task['task_id']}/schemas/{task['task_schema_id']}/versions/1/deploy",
        json={"environment": "dev", "provider_config_id": org_settings_id},
    )
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "provider_does_not_support_model"


async def test_deploy_provider_config_task_run_failed(test_client: IntegrationTestClient):
    test_client.mock_mistralai_completion()
    res = await test_client.int_api_client.post(
        "/chiefofstaff.ai/organization/settings/providers",
        json={"provider": "mistral_ai", "api_key": "sk-ant-api03-..."},
    )
    org_settings_id = result_or_raise(res)["id"]
    assert len(test_client.httpx_mock.get_requests(url="https://api.mistral.ai/v1/chat/completions")) == 1

    test_client.reset_httpx_mock()
    task = await _prepare_deploy_with_config(test_client)
    # Deploy
    test_client.mock_mistralai_completion_failure()
    res = await test_client.int_api_client.post(
        f"/chiefofstaff.ai/agents/{task['task_id']}/schemas/{task['task_schema_id']}/versions/1/deploy",
        json={"environment": "dev", "provider_config_id": org_settings_id},
    )
    assert res.status_code == 400
    assert res.json() == {
        "error": {
            "code": "bad_request",
            "message": "The provider config did not run on the given task",
            "status_code": 400,
        },
    }
