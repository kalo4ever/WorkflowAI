import datetime

from pydantic import BaseModel, Field

from core.domain.major_minor import MajorMinor
from core.storage.mongo.models.base_document import BaseDocumentWithID
from core.utils.fields import datetime_factory


class TaskGroupSemverDocument(BaseDocumentWithID):
    task_id: str = ""
    similarity_hash: str = ""
    major: int = 0
    max_minor: int = 0

    class Minor(BaseModel):
        minor: int
        properties_hash: str
        created_at: datetime.datetime = Field(default_factory=datetime_factory)

    minors: list[Minor] = []

    def to_semver(self, property_hash: str):
        for minor in self.minors:
            if minor.properties_hash == property_hash:
                return MajorMinor(major=self.major, minor=minor.minor)
        return None
