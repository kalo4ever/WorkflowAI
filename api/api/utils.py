import json
import logging
import os
import re
from contextvars import ContextVar
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

from api.services.metrics import BetterStackMetricsService
from core.domain.error_response import ErrorCode, ErrorResponse
from core.domain.metrics import Metric
from core.utils.dicts import blacklist_keys


def convert_error_response(res: ErrorResponse, headers: dict[str, Any] | None = None):
    return JSONResponse(
        content=res.model_dump(mode="json", exclude_none=True, by_alias=True),
        status_code=res.error.status_code,
        headers=headers,
    )


def error_json_response(
    status_code: int,
    msg: str,
    code: ErrorCode,
    details: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
) -> JSONResponse:
    return convert_error_response(
        ErrorResponse.with_status_code(
            status_code=status_code,
            msg=msg,
            code=code,
            details=details,
        ),
        headers,
    )


def get_transaction_name(request: Request) -> str:
    current_route: Any = request.scope.get("route")
    return current_route.path if current_route else request.url.path


print_blacklist = {
    re.compile(k)
    for k in [
        r"^task_input$",
        r"^task_output$",
        r".*key.*",
        r".*credentials.*",
        r".*secret.*",
        r".*token.*",
    ]
}


async def log_start(
    request: Request,
    request_id_var: ContextVar[str | None],
    logger: logging.Logger,
    extra: dict[str, Any] | None = None,
):
    logger.info(
        f"--> {request_id_var.get()} {request.method} {request.url.path}?{request.url.query}",  # noqa: G004
        extra=extra,
    )


async def log_start_with_body(request: Request, request_id_var: ContextVar[str | None], logger: logging.Logger):
    body: bytes | None = None
    extra: dict[str, Any] | None = None
    body = await request.body()
    if body:
        try:
            printed_body: Any = blacklist_keys(json.loads(body), "...", *print_blacklist)
        except Exception:
            printed_body = body.decode()[:200]
        extra = {"body": printed_body[:1000] if printed_body and len(printed_body) > 1000 else printed_body}
    await log_start(request, request_id_var, logger, extra)


async def log_end(
    request: Request,
    duration: float,
    status_code: int,
    logger: logging.Logger,
    error: Exception | None = None,
    extra: dict[str, Any] | None = None,
):
    fn = logger.info if error is None else logger.error
    fn(
        f"<-- {request.method} {request.url.path} {status_code}",
        extra=extra,
    )

    route = get_transaction_name(request)
    await Metric(
        name="latency",
        gauge=duration,
        tags={"status_code": status_code, "route": route, "tenant": request.path_params.get("tenant", "")},
    ).send()


async def setup_metrics():
    if betterstack_api_key := os.getenv("BETTERSTACK_API_KEY"):
        metrics_service = BetterStackMetricsService(
            tags={"e": os.getenv("ENV_NAME", "local"), "v": os.getenv("RELEASE_NAME", "unknown")},
            betterstack_api_key=betterstack_api_key,
            betterstack_api_url=os.getenv("BETTERSTACK_API_URL"),
        )
        await metrics_service.start()
        Metric.sender = metrics_service.send_metric
    else:
        metrics_service = None
    return metrics_service


async def close_metrics(metrics_service: BetterStackMetricsService | None):
    if metrics_service:
        await metrics_service.close()
        Metric.reset_sender()
