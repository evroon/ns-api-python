from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel

from models.base import ResponseModel, QueryParams
from models.stations import Station


class DelayInfo(BaseModel):
    origin: Station
    destination: Station
    delay: timedelta
    planned_departure: datetime
    actual_departure: datetime

    def __str__(self) -> str:
        origin_name = self.origin.names.long
        dest_name = self.destination.names.long
        return f"{origin_name} - {dest_name}: {self.delay} at {self.actual_departure}"


class Departure(BaseModel):
    direction: str
    name: str
    plannedDateTime: datetime
    plannedTimeZoneOffset: int
    actualDateTime: datetime
    actualTimeZoneOffset: int
    plannedTrack: str | None
    trainCategory: str
    cancelled: bool
    departureStatus: str
    delay: Optional[DelayInfo]

    def __str__(self) -> str:
        actual_formatted = datetime.strftime(self.actualDateTime, "%H:%M")
        return f"{self.trainCategory: <3} - {self.direction: <32} at {actual_formatted} on track {self.plannedTrack: >2}"


class DeparturePayloadModel(BaseModel):
    departures: List[Departure]


class DepartureResponseModel(ResponseModel):
    payload: DeparturePayloadModel


class DepartureParams(QueryParams):
    station: str
