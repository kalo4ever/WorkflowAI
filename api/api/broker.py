import logging
import os
from typing import Any

from taskiq import SimpleRetryMiddleware, TaskiqEvents, TaskiqMessage, TaskiqResult, TaskiqState
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend
from typing_extensions import override

from api.common import setup
from api.errors import configure_scope_for_error
from api.utils import close_metrics, setup_metrics
from core.domain.errors import InternalError
from core.domain.metrics import Metric

setup()


def _broker():
    broker_url = os.environ["JOBS_BROKER_URL"]
    if broker_url.startswith("redis"):
        return ListQueueBroker(url=broker_url).with_result_backend(
            # We expire results after 2 hours
            RedisAsyncResultBackend[Any](redis_url=broker_url, result_ex_time=2 * 60 * 60),
        )

    if broker_url.startswith("memory://"):
        from taskiq import InMemoryBroker

        return InMemoryBroker()
    raise ValueError(f"Unknown broker URL: {broker_url}")


_logger = logging.getLogger(__name__)
_logger.propagate = True


class ErrorMiddleware(SimpleRetryMiddleware):
    @override
    async def on_error(
        self,
        message: TaskiqMessage,
        result: TaskiqResult[Any],
        exception: BaseException,
    ):
        is_fatal = isinstance(exception, InternalError) and exception.fatal
        msg = (
            f"Fatal error while executing task {message.task_name}"
            if is_fatal
            else f"Retriable Error while executing task {message.task_name}"
        )
        with configure_scope_for_error(
            exception,
            {"job": True, "transaction": message.task_name},
            extras={"args": message.args, "kwargs": message.kwargs},
        ):
            _logger.exception(msg, exc_info=exception)

        if is_fatal:
            return

        await Metric(
            name="job_retry",
            counter=1,
            tags={"task_name": message.task_name},
        ).send()
        await super().on_error(message, result, exception)

    @override
    async def post_execute(
        self,
        message: "TaskiqMessage",
        result: "TaskiqResult[Any]",
    ) -> None:
        """
        This function tracks number of errors and success executions.

        :param message: received message.
        :param result: result of the execution.
        """
        await Metric(
            name="job_execution_time",
            gauge=result.execution_time,
            tags={"task_name": message.task_name, "error": result.is_err},
        ).send()


broker = _broker().with_middlewares(
    # TODO: add backoff and jitter
    ErrorMiddleware(default_retry_count=3),
)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def worker_startup(state: TaskiqState):
    state.metrics_service = await setup_metrics()


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def worker_shutdown(state: TaskiqState):
    await close_metrics(state.metrics_service)
    from api.services.security_svc import SecurityService

    await SecurityService.wait_for_background_tasks()
