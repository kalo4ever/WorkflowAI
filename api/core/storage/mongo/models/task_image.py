from typing import Self

from core.domain.task_image import TaskImage
from core.storage.mongo.models.base_document import BaseDocument


class TaskImageDocument(BaseDocument):
    task_id: str = ""
    image_data: bytes = b""
    compressed_image_data: bytes = b""

    @classmethod
    def from_resource(
        cls,
        tenant: str,
        ressource: TaskImage,
    ) -> Self:
        return cls(
            tenant=tenant,
            task_id=ressource.task_id,
            image_data=ressource.image_data,
            compressed_image_data=ressource.compressed_image_data,
        )

    def to_resource(self) -> TaskImage:
        return TaskImage(
            task_id=self.task_id,
            image_data=self.image_data,
            compressed_image_data=self.compressed_image_data,
        )
