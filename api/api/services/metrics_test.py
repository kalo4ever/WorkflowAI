import asyncio
from unittest.mock import Mock

import pytest

from api.services.metrics import BetterStackMetricsService
from core.domain.metrics import Metric
from core.storage.betterstack.betterstack_client import BetterStackClient


@pytest.fixture()
async def betterstack_client():
    return Mock(spec=BetterStackClient)


@pytest.fixture()
async def metrics_service(betterstack_client: Mock):
    svc = BetterStackMetricsService(
        tags={"a": "b"},
        betterstack_api_key="test",
        send_interval_seconds=0.2,
        max_buffer_size=2,
        client=betterstack_client,
    )
    await svc.start()
    yield svc
    await svc.close()


class TestMetricsService:
    async def test_send_metrics_buffered(self, metrics_service: BetterStackMetricsService, betterstack_client: Mock):
        m1 = Metric(name="test", gauge=1)
        m2 = Metric(name="test1", gauge=2)
        await metrics_service.send_metric(m1)
        await metrics_service.send_metric(m2)
        betterstack_client.send_metrics.assert_not_called()

        await asyncio.sleep(0.01)

        betterstack_client.send_metrics.assert_called_once_with(
            [m1, m2],
            {"a": "b"},
        )

    async def test_send_metrics_buffer_not_full(
        self,
        metrics_service: BetterStackMetricsService,
        betterstack_client: Mock,
    ):
        m1 = Metric(name="test", gauge=1)
        await metrics_service.send_metric(m1)
        betterstack_client.send_metrics.assert_not_called()

        await asyncio.sleep(0.10)

        # not enough time has passed to send the metrics
        betterstack_client.send_metrics.assert_not_called()

        await asyncio.sleep(0.11)

        betterstack_client.send_metrics.assert_called_once_with([m1], {"a": "b"})
