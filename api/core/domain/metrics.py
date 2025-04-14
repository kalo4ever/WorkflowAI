import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any, ClassVar

from pydantic import BaseModel, Field


async def _noop_sender(metric: "Metric", *args: Any, **kwargs: Any):
    logging.getLogger(__name__).debug("Noop sender for metric %s: %s", metric.name, metric.gauge or metric.counter)


class Metric(BaseModel):
    name: str
    timestamp: float = Field(default_factory=time.time)
    tags: dict[str, int | str | float | bool] = Field(default_factory=dict)

    gauge: float | None = None
    counter: int | None = None

    sender: ClassVar[Callable[["Metric"], Awaitable[None]]] = _noop_sender

    async def send(self):
        await self.__class__.sender(self)

    @classmethod
    def reset_sender(cls):
        cls.sender = _noop_sender


async def send_counter(name: str, value: int = 1, **tags: int | str | float | bool | None):
    try:
        await Metric(name=name, counter=value, tags={k: v for k, v in tags.items() if v is not None}).send()
    except Exception:
        logging.getLogger(__name__).exception("Failed to send counter metric %s: %s", name, tags)


async def send_gauge(name: str, value: float, timestamp: float | None = None, **tags: int | str | float | bool | None):
    try:
        await Metric(
            name=name,
            gauge=value,
            timestamp=timestamp or time.time(),
            tags={k: v for k, v in tags.items() if v is not None},
        ).send()
    except Exception:
        logging.getLogger(__name__).exception("Failed to send gauge metric %s: %s", name, tags)
