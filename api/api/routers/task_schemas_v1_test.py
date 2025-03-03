import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from api.dependencies.latest_task_variant import latest_task_variant_id
from api.routers.task_schemas_v1 import SearchFields
from core.domain.search_query import SearchField, SearchFieldOption, SearchOperator
from core.domain.task_variant import SerializableTaskVariant
from tests.models import task_variant


@pytest.fixture
def patched_task_dep(test_app: FastAPI):
    mocked_variant = task_variant()
    mocked_variant.input_schema.json_schema["properties"] = {"name": {"type": "string"}}
    test_app.dependency_overrides[latest_task_variant_id] = lambda: mocked_variant
    return mocked_variant


class TestCheckInstructions:
    async def test_not_a_template(
        self,
        test_api_client: AsyncClient,
    ):
        response = await test_api_client.post(
            "/v1/_/agents/task_id/schemas/1/instructions/check",
            json={"instructions": "Hello!"},
        )
        assert response.status_code == 200
        assert response.json() == {"is_template": False, "is_valid": True}

    async def test_invalid_template(
        self,
        test_api_client: AsyncClient,
    ):
        response = await test_api_client.post(
            "/v1/_/agents/task_id/schemas/1/instructions/check",
            json={"instructions": "Hello, {{ name }!"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "is_template": True,
            "is_valid": False,
            "error": {"message": "unexpected '}'", "line_number": 1},
        }

    async def test_check_instructions_success(
        self,
        test_api_client: AsyncClient,
        patched_task_dep: SerializableTaskVariant,
    ):
        response = await test_api_client.post(
            "/v1/_/agents/task_id/schemas/1/instructions/check",
            json={"instructions": "Hello, {{ name }}!"},
        )
        assert response.status_code == 200
        assert response.json() == {"is_template": True, "is_valid": True}

    async def test_check_instructions_missing_keys(
        self,
        test_api_client: AsyncClient,
        patched_task_dep: SerializableTaskVariant,
    ):
        response = await test_api_client.post(
            "/v1/_/agents/task_id/schemas/1/instructions/check",
            json={"instructions": "Hello, {{ name }} how are {{ age }}!"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "is_template": True,
            "is_valid": False,
            "error": {
                "message": "The template is referencing keys that are not present in the input",
                "missing_keys": ["age"],
            },
        }


# TODO[test]: make sure we have similar tests for the v1 endpoint
# class TestGetModelsPerTaskSchema:
#     @pytest.fixture(scope="function")
#     def mock_local_provider_factory(self) -> Mock:
#         return Mock(spec=LocalProviderFactory)

#     async def test_get_models_success_simple_task(
#         self,
#         test_api_client: AsyncClient,
#         mock_storage: Mock,
#         mock_models_service: Mock,
#     ):
#         # Mock the task variant retrieval
#         mock_storage.task_variant_latest_by_schema_id.return_value = task_variant()

#         # Mock the cost estimates
#         mock_models_service.get_cost_estimates.return_value = {
#             (Model.GPT_4O_2024_08_06.value, "openai"): 0.02,
#             (Model.LLAMA_3_2_3B.value, "fireworks"): 0.001,
#             (Model.LLAMA_3_2_90B.value, "google"): 0.015,
#         }

#         # Make the request
#         response = await test_api_client.get("/_/agents/task_id/schemas/1/models")

#         assert response.status_code == 200
#         json_response = response.json()
#         assert "models" in json_response

#         assert len(json_response["models"]) == GLOBAL_AVAILABLE_MODELS_COUNT

#         compatible_provider_models = [
#             provider
#             for model in json_response["models"]
#             for provider in model["providers"]
#             if not provider["is_not_supported"]
#         ]

#         assert (
#             len(compatible_provider_models) == 84
#         )  # Some models have multiple providers (ex: Llama 3.1 405b) -1 for Gpt 4o audio preview
#         assert Model.GPT_40_AUDIO_PREVIEW_2024_10_01 not in [m["id"] for m in compatible_provider_models]

#         model1 = next((m for m in json_response["models"] if m["id"] == Model.GPT_4O_2024_08_06.value), None)
#         assert model1 is not None
#         assert set(model1["modes"]) == {"images", "text"}
#         del model1["modes"]
#         assert model1 == {
#             "id": "gpt-4o-2024-08-06",
#             "name": "GPT-4o (2024-08-06)",
#             "providers": [
#                 {
#                     "id": "openai",
#                     "name": "Open AI",
#                     "average_cost_per_run_usd": 0.02,
#                     "is_not_supported": False,
#                     "is_not_supported_reason": None,
#                 },
#                 {
#                     "id": "azure_openai",
#                     "name": "Azure Open AI",
#                     "average_cost_per_run_usd": None,
#                     "is_not_supported": False,
#                     "is_not_supported_reason": None,
#                 },
#             ],
#         }

#         model2 = next((m for m in json_response["models"] if m["id"] == Model.LLAMA_3_2_3B.value), None)
#         assert model2 is not None
#         assert set(model2["modes"]) == set()
#         del model2["modes"]
#         assert model2 == {
#             "id": "llama-3.2-3b",
#             "name": "Llama 3.2 (3B) Instruct",
#             "providers": [
#                 {
#                     "id": "fireworks",
#                     "name": "Fireworks AI",
#                     "average_cost_per_run_usd": 0.001,
#                     "is_not_supported": False,
#                     "is_not_supported_reason": None,
#                 },
#                 {
#                     "id": "amazon_bedrock",
#                     "name": "Amazon Bedrock",
#                     "average_cost_per_run_usd": None,
#                     "is_not_supported": False,
#                     "is_not_supported_reason": None,
#                 },
#             ],
#         }

#         model3 = next((m for m in json_response["models"] if m["id"] == Model.LLAMA_3_2_90B.value), None)
#         assert model3 is not None
#         assert set(model3["modes"]) == {"images"}
#         del model3["modes"]
#         assert model3["id"] == "llama-3.2-90b"
#         assert model3["name"] == "Llama 3.2 (90B) Instruct"
#         assert len(model3["providers"]) == 2
#         assert {
#             "id": "google",
#             "name": "Google",
#             "average_cost_per_run_usd": 0.015,
#             "is_not_supported": False,
#             "is_not_supported_reason": None,
#         } in model3["providers"]
#         assert {
#             "average_cost_per_run_usd": None,
#             "id": "amazon_bedrock",
#             "is_not_supported": False,
#             "is_not_supported_reason": None,
#             "name": "Amazon Bedrock",
#         } in model3["providers"]

#     async def test_get_models_success_single_file_task(
#         self,
#         test_api_client: AsyncClient,
#         mock_storage: Mock,
#         mock_models_service: Mock,
#     ):
#         # Mock the task variant retrieval
#         mock_storage.task_variant_latest_by_schema_id.return_value = task_variant_with_single_file()

#         # Mock the cost estimates
#         mock_models_service.get_cost_estimates.return_value = {
#             (Model.GPT_4O_2024_08_06.value, "openai"): 0.02,
#             (Model.LLAMA_3_2_3B.value, "fireworks"): 0.001,
#             (Model.LLAMA_3_2_90B.value, "google"): 0.015,
#         }

#         # Make the request
#         response = await test_api_client.get("/_/agents/task_id/schemas/1/models")

#         assert response.status_code == 200
#         json_response = response.json()
#         assert "models" in json_response

#         assert len(json_response["models"]) == GLOBAL_AVAILABLE_MODELS_COUNT

#         compatible_models = [
#             provider
#             for model in json_response["models"]
#             for provider in model["providers"]
#             if not provider["is_not_supported"]
#         ]

#         # We do not filter out any model for document based task because all models support text documents
#         assert len(compatible_models) == 84
#         assert Model.GPT_40_AUDIO_PREVIEW_2024_10_01 not in [m["id"] for m in compatible_models]
#         model1 = next((m for m in json_response["models"] if m["id"] == Model.GPT_4O_2024_08_06.value), None)
#         assert model1 is not None
#         assert set(model1["modes"]) == {"images", "text"}
#         del model1["modes"]
#         assert model1 == {
#             "id": "gpt-4o-2024-08-06",
#             "name": "GPT-4o (2024-08-06)",
#             "providers": [
#                 {
#                     "id": "openai",
#                     "name": "Open AI",
#                     "average_cost_per_run_usd": 0.02,
#                     "is_not_supported": False,
#                     "is_not_supported_reason": None,
#                 },
#                 {
#                     "id": "azure_openai",
#                     "name": "Azure Open AI",
#                     "average_cost_per_run_usd": None,
#                     "is_not_supported": False,
#                     "is_not_supported_reason": None,
#                 },
#             ],
#         }

#         model2 = next((m for m in json_response["models"] if m["id"] == Model.LLAMA_3_2_3B.value), None)
#         assert model2 is not None
#         assert set(model2["modes"]) == set()
#         del model2["modes"]
#         assert model2 == {
#             "id": "llama-3.2-3b",
#             "name": "Llama 3.2 (3B) Instruct",
#             "providers": [
#                 {
#                     "id": "fireworks",
#                     "name": "Fireworks AI",
#                     "average_cost_per_run_usd": 0.001,
#                     "is_not_supported": False,
#                     "is_not_supported_reason": None,
#                 },
#                 {
#                     "id": "amazon_bedrock",
#                     "name": "Amazon Bedrock",
#                     "average_cost_per_run_usd": None,
#                     "is_not_supported": False,
#                     "is_not_supported_reason": None,
#                 },
#             ],
#         }

#         model3 = next((m for m in json_response["models"] if m["id"] == Model.LLAMA_3_2_90B.value), None)
#         assert model3 is not None
#         assert set(model3["modes"]) == {"images"}
#         del model3["modes"]
#         assert model3["id"] == "llama-3.2-90b"
#         assert model3["name"] == "Llama 3.2 (90B) Instruct"
#         assert len(model3["providers"]) == 2
#         assert {
#             "id": "google",
#             "name": "Google",
#             "average_cost_per_run_usd": 0.015,
#             "is_not_supported": False,
#             "is_not_supported_reason": None,
#         } in model3["providers"]
#         assert {
#             "average_cost_per_run_usd": None,
#             "id": "amazon_bedrock",
#             "is_not_supported": False,
#             "is_not_supported_reason": None,
#             "name": "Amazon Bedrock",
#         } in model3["providers"]

#     async def test_get_models_success_multiple_file_task(
#         self,
#         test_api_client: AsyncClient,
#         mock_storage: Mock,
#         mock_models_service: Mock,
#     ):
#         # Mock the task variant retrieval
#         mock_storage.task_variant_latest_by_schema_id.return_value = task_variant_with_multiple_images()

#         # Mock the cost estimates
#         mock_models_service.get_cost_estimates.return_value = {
#             (Model.GPT_4O_2024_08_06.value, "openai"): 0.02,
#             (Model.LLAMA_3_2_3B.value, "fireworks"): 0.001,
#             (Model.LLAMA_3_2_90B.value, "google"): 0.015,
#         }

#         # Make the request
#         response = await test_api_client.get("/_/agents/task_id/schemas/1/models")

#         assert response.status_code == 200
#         json_response = response.json()
#         assert "models" in json_response

#         assert len(json_response["models"]) == GLOBAL_AVAILABLE_MODELS_COUNT

#         compatible_models = [
#             provider
#             for model in json_response["models"]
#             for provider in model["providers"]
#             if not provider["is_not_supported"]
#         ]
#         assert len(compatible_models) == 51

#         model1 = next((m for m in json_response["models"] if m["id"] == Model.GPT_4O_2024_08_06.value), None)
#         assert model1 is not None
#         assert set(model1["modes"]) == {"images", "text"}
#         del model1["modes"]
#         assert model1 == {
#             "id": "gpt-4o-2024-08-06",
#             "name": "GPT-4o (2024-08-06)",
#             "providers": [
#                 {
#                     "id": "openai",
#                     "name": "Open AI",
#                     "average_cost_per_run_usd": 0.02,
#                     "is_not_supported": False,
#                     "is_not_supported_reason": None,
#                 },
#                 {
#                     "id": "azure_openai",
#                     "name": "Azure Open AI",
#                     "average_cost_per_run_usd": None,
#                     "is_not_supported": False,
#                     "is_not_supported_reason": None,
#                 },
#             ],
#         }

#         model2 = next((m for m in json_response["models"] if m["id"] == Model.LLAMA_3_2_3B.value), None)
#         assert model2 is not None
#         assert set(model2["modes"]) == set()
#         del model2["modes"]
#         assert model2 == {
#             "id": "llama-3.2-3b",
#             "name": "Llama 3.2 (3B) Instruct",
#             "providers": [
#                 {
#                     "id": "fireworks",
#                     "name": "Fireworks AI",
#                     "average_cost_per_run_usd": 0.001,
#                     "is_not_supported": False,
#                     "is_not_supported_reason": None,
#                 },
#                 {
#                     "id": "amazon_bedrock",
#                     "name": "Amazon Bedrock",
#                     "average_cost_per_run_usd": None,
#                     "is_not_supported": True,
#                     "is_not_supported_reason": "Llama 3.2 (3B) Instruct does not support input images",
#                 },
#             ],
#         }

#         model3 = next((m for m in json_response["models"] if m["id"] == Model.LLAMA_3_2_90B.value), None)
#         assert model3 is not None
#         assert set(model3["modes"]) == {"images"}
#         del model3["modes"]
#         assert model3["id"] == "llama-3.2-90b"
#         assert model3["name"] == "Llama 3.2 (90B) Instruct"
#         assert len(model3["providers"]) == 2
#         assert {
#             "id": "google",
#             "name": "Google",
#             "average_cost_per_run_usd": 0.015,
#             "is_not_supported": True,
#             "is_not_supported_reason": "Llama 3.2 (90B) Instruct does not support multiple images in input",
#         } in model3["providers"]
#         assert {
#             "average_cost_per_run_usd": None,
#             "id": "amazon_bedrock",
#             "is_not_supported": True,
#             "is_not_supported_reason": "Llama 3.2 (90B) Instruct does not support multiple images in input",
#             "name": "Amazon Bedrock",
#         } in model3["providers"]

#     async def test_get_models_success_task_with_audio(
#         self,
#         test_api_client: AsyncClient,
#         mock_storage: Mock,
#         mock_models_service: Mock,
#     ):
#         # Mock the task variant retrieval
#         mock_storage.task_variant_latest_by_schema_id.return_value = task_variant_with_audio_file()

#         # Mock the cost estimates
#         mock_models_service.get_cost_estimates.return_value = {
#             (Model.GEMINI_1_5_PRO_002.value, "google"): 0.02,
#             (Model.GPT_4O_2024_08_06.value, "openai"): 0.01,
#         }

#         # Make the request
#         response = await test_api_client.get("/_/agents/task_id/schemas/1/models")

#         assert response.status_code == 200
#         json_response = response.json()
#         assert "models" in json_response

#         assert len(json_response["models"]) == GLOBAL_AVAILABLE_MODELS_COUNT

#         compatible_models = [
#             provider
#             for model in json_response["models"]
#             for provider in model["providers"]
#             if not provider["is_not_supported"]
#         ]
#         assert len(compatible_models) == 18  # only non-decommisioned Gemini models & GPT-4o Audio Preview support audio

#         compatible_model = next((m for m in json_response["models"] if m["id"] == Model.GEMINI_1_5_PRO_002.value), None)
#         assert compatible_model is not None
#         assert set(compatible_model["modes"]) == {"audio", "images", "text"}
#         del compatible_model["modes"]
#         assert {
#             "id": "google",
#             "name": "Google",
#             "average_cost_per_run_usd": 0.02,
#             "is_not_supported": False,
#             "is_not_supported_reason": None,
#         } in compatible_model["providers"]
#         assert {
#             "id": "google_gemini",
#             "name": "Google Gemini API",
#             "average_cost_per_run_usd": None,
#             "is_not_supported": False,
#             "is_not_supported_reason": None,
#         } in compatible_model["providers"]

#         non_compatible_model = next(
#             (m for m in json_response["models"] if m["id"] == Model.GPT_4O_2024_08_06.value),
#             None,
#         )
#         assert non_compatible_model is not None
#         assert set(non_compatible_model["modes"]) == {"images", "text"}
#         del non_compatible_model["modes"]
#         assert non_compatible_model == {
#             "id": "gpt-4o-2024-08-06",
#             "name": "GPT-4o (2024-08-06)",
#             "providers": [
#                 {
#                     "id": "openai",
#                     "name": "Open AI",
#                     "average_cost_per_run_usd": 0.01,
#                     "is_not_supported": True,
#                     "is_not_supported_reason": "GPT-4o (2024-08-06) does not support input audio",
#                 },
#                 {
#                     "id": "azure_openai",
#                     "name": "Azure Open AI",
#                     "average_cost_per_run_usd": None,
#                     "is_not_supported": True,
#                     "is_not_supported_reason": "GPT-4o (2024-08-06) does not support input audio",
#                 },
#             ],
#         }

#     async def test_get_models_task_not_found(
#         self,
#         test_api_client: AsyncClient,
#         mock_storage: Mock,
#     ):
#         # Mock storage to raise ObjectNotFoundException
#         mock_storage.task_variant_latest_by_schema_id.side_effect = ObjectNotFoundException("Task not found")

#         # Make the request with an invalid task_id
#         response = await test_api_client.get("/_/agents/invalid_task_id/schemas/1/models")

#         assert response.status_code == 404
#         json_response = response.json()
#         assert json_response["detail"] == "Task variant not found"


class TestSearchFieldsFromDomain:
    async def test_search_fields_from_domain(self, test_api_client: AsyncClient):
        field = SearchFieldOption(
            field_name=SearchField.METADATA,
            operators=[SearchOperator.IS],
            type="string",
            key_path="f1",
        )
        assert SearchFields.Item.from_domain(field).model_dump(exclude_none=True) == {
            "field_name": "metadata.f1",
            "operators": ["is"],
            "type": "string",
        }
