from typing import Any

from core.domain.fields.file import DomainUploadFile, File


def event_router(*args: Any, **kwargs: Any) -> None:  # type: ignore
    pass


class NoopEncryption:
    def encrypt(self, value: str) -> str:
        return value

    def decrypt(self, value: str) -> str:
        return value


class NoopMetricsService:
    from core.domain.metrics import Metric

    async def start(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def send_metric(self, metric: Metric) -> None:
        pass


class NoopFileStorage:
    async def store_file(self, file: File | DomainUploadFile, folder_path: str) -> str:
        return ""
