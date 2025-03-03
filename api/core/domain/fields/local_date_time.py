import datetime

from pydantic import BaseModel, Field

from .zone_info import TimezoneInfo


class DatetimeLocal(BaseModel):
    """This class represents a local datetime, with a datetime and a timezone."""

    date: datetime.date = Field(
        description="The date of the local datetime.",
        json_schema_extra={"format": "date"},
    )
    local_time: datetime.time = Field(
        description="The time of the local datetime without timezone info.",
        json_schema_extra={"format": "time"},
    )
    timezone: TimezoneInfo = Field(
        description="The timezone of the local time, in the 'Europe/Paris', 'America/New_York' format.",
    )

    def to_datetime(self) -> datetime.datetime:
        """Builds a 'datetime' object from the local 'date', local 'time' and 'timezone'."""

        time_with_tz = self.local_time.replace(tzinfo=self.timezone)
        return datetime.datetime.combine(self.date, time_with_tz)
