from unittest.mock import Mock, patch

from httpx import AsyncClient

from core.storage.backend_storage import BackendStorage
from core.utils import no_op


class TestReadiness:
    async def test_success(self, test_api_client: AsyncClient, mock_user_dep: Mock):
        mock_storage = Mock(spec=BackendStorage)
        mock_storage.is_ready.return_value = True

        # Mock no_op.event_router
        mock_event_router = Mock()
        no_op.event_router = mock_event_router

        with patch("api.services.storage.storage_for_tenant", return_value=mock_storage):
            res = await test_api_client.get("/probes/readiness", headers={"Authorization": ""})
            assert res.status_code == 200

            mock_storage.is_ready.assert_called_once()
            mock_user_dep.assert_not_called()
            # Ensure no_op.event_router is used
            mock_event_router.assert_not_called()
