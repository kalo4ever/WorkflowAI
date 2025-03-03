import asyncio
import logging
from typing import Any, Coroutine, Protocol

from core.domain.metrics import Metric
from core.storage.betterstack.betterstack_client import BetterStackClient


class MetricsService(Protocol):
    async def start(self) -> None: ...
    async def close(self) -> None: ...
    async def send_metric(self, metric: Metric) -> None: ...


class BetterStackMetricsService:
    def __init__(
        self,
        tags: dict[str, str],
        betterstack_api_key: str,
        send_interval_seconds: float = 30,
        max_buffer_size: int = 50,
        client: BetterStackClient | None = None,
    ):
        self._tasks: set[asyncio.Task[None]] = set()
        self._client = client or BetterStackClient(betterstack_api_key)
        self._tags = tags
        self._buffer: list[Metric] = []
        self._logger = logging.getLogger(__name__)
        self._send_interval_seconds = send_interval_seconds
        self._buffer_lock = asyncio.Lock()
        self._max_buffer_size = max_buffer_size
        self._schedule_task: asyncio.Task[None] | None = None
        self._started = False

    async def start(self):
        self._started = True
        if not self._schedule_task:
            self._schedule_task = asyncio.create_task(self._schedule_send_metrics())

    async def close(self) -> None:
        self._started = False

        if self._schedule_task:
            self._schedule_task.cancel()

        await asyncio.gather(*self._tasks)
        await self._client.close()

    async def _send_metrics_now(self) -> None:
        # We will not have race conditions on the buffer since we are
        # single threaded
        async with self._buffer_lock:
            metrics = self._buffer
            self._buffer = []

        if not metrics:
            return

        try:
            await self._client.send_metrics(metrics, self._tags)
        except Exception as e:
            self._logger.error("Failed to send metrics to BetterStack", exc_info=e, extra={"metrics": metrics})

    async def _schedule_send_metrics(self) -> None:
        while self._started:
            # Send metrics every 10 seconds
            await asyncio.sleep(self._send_interval_seconds)
            # Adding as a task so we can cancel the schedule without
            # affecting the send metrics task
            self._add_task(self._send_metrics_now())

    def _add_task(self, task: Coroutine[Any, Any, None]):
        t = asyncio.create_task(task)
        self._tasks.add(t)
        t.add_done_callback(self._tasks.remove)

    async def send_metric(self, metric: Metric) -> None:
        self._buffer.append(metric)
        # Purging the buffer if it is too big
        if len(self._buffer) >= self._max_buffer_size:
            self._add_task(self._send_metrics_now())
            return
