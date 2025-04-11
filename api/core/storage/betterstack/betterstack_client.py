import asyncio
import logging
from typing import NotRequired, TypedDict

import httpx

from core.domain.errors import InternalError
from core.domain.metrics import Metric


class _GaugeMetric(TypedDict):
    value: float


class _CounterMetric(TypedDict):
    value: int


class _MetricRequest(TypedDict):
    name: str
    dt: int
    gauge: NotRequired[_GaugeMetric]
    counter: NotRequired[_CounterMetric]
    tags: NotRequired[dict[str, int | str | float | bool]]


class BetterStackClient:
    def __init__(
        self,
        betterstack_api_key: str,
        betterstack_api_url: str | None = None,
        default_retry_delay: float = 10.0,
    ):
        self._betterstack_api_key = betterstack_api_key
        self._client = httpx.AsyncClient(base_url=betterstack_api_url or "https://in.logs.betterstack.com")
        self._logger = logging.getLogger(__name__)
        self._default_retry_delay = default_retry_delay

    async def close(self) -> None:
        await self._client.aclose()

    def _metric_to_request(self, metric: Metric, tags: dict[str, str]) -> _MetricRequest:
        req: _MetricRequest = {
            "name": metric.name,
            "dt": int(metric.timestamp * 1000),
            "tags": {**tags, **metric.tags},
        }
        if metric.gauge is not None:
            req["gauge"] = {"value": metric.gauge}
        elif metric.counter is not None:
            req["counter"] = {"value": metric.counter}
        return req

    def _parse_retry_after(self, retry_after: str | None) -> float:
        if retry_after is None:
            return self._default_retry_delay
        try:
            return float(retry_after)
        except ValueError:
            self._logger.warning("Failed to parse Retry-After header", extra={"retry_after": retry_after})
            return self._default_retry_delay

    async def send_metrics(self, metrics: list[Metric], tags: dict[str, str], retry_count: int = 3) -> None:
        reqs = [self._metric_to_request(metric, tags=tags) for metric in metrics]

        for i in range(retry_count):
            try:
                response = await self._client.post(
                    "/metrics",
                    json=reqs,
                    headers={"Authorization": f"Bearer {self._betterstack_api_key}"},
                )
                response.raise_for_status()
                return
            except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as e:
                if i == retry_count - 1:
                    raise e
                self._logger.warning(
                    "Failed retry to send metrics to BetterStack",
                    exc_info=e,
                    extra={"metrics": reqs, "retry_count": retry_count},
                )
                if isinstance(e, httpx.HTTPStatusError):
                    retry_after = self._parse_retry_after(e.response.headers.get("Retry-After"))
                else:
                    retry_after = self._default_retry_delay
                await asyncio.sleep(retry_after)

        # We should never reach this line
        raise InternalError("Failed to send metrics to BetterStack")
