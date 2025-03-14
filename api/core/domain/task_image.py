from pydantic import BaseModel


class TaskImage(BaseModel):
    task_id: str
    image_data: bytes
    compressed_image_data: bytes
