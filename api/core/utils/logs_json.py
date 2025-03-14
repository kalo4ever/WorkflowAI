from typing import Any, override

from pythonjsonlogger import jsonlogger


class CappedJsonFormatter(jsonlogger.JsonFormatter):
    def __init__(self, max_length: int = 400, reserved_attrs: list[str] | None = None, *args: Any, **kwargs: Any):
        reserved_attrs = reserved_attrs or ["taskName", *jsonlogger.RESERVED_ATTRS]
        super().__init__(*args, reserved_attrs=reserved_attrs, **kwargs)  # pyright: ignore [reportUnknownMemberType]

        self.max_log_size = max_length

    @override
    def format(self, *args: Any, **kwargs: Any):
        formatted = super().format(*args, **kwargs)
        if len(formatted) > self.max_log_size:
            # Capturing the error on sentry directly
            # Not capturing on sentry for now, this is called a lot
            # TODO: add back, a lot of noise comes from exc_info that are added to the log
            # We should just remove them from the payload since they are already on sentry
            # with configure_scope() as scope:
            #     scope.set_extra("log", formatted[: self.max_log_size])
            #     capture_message("Log message is too long", level="warning")
            formatted = formatted[: self.max_log_size]

        return formatted
