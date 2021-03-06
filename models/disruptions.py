from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from models.base import ResponseModel, QueryParams


class DisruptionType(Enum):
    CALAMITY = "CALAMITY"
    DISRUPTION = "DISRUPTION"
    MAINTENANCE = "MAINTENANCE"


class Disruption(BaseModel):
    id: str
    type: DisruptionType
    title: str
    isActive: str
    topic: Optional[str]
    registrationTime: Optional[datetime]
    releaseTime: Optional[datetime]
    start: Optional[datetime]
    end: Optional[datetime]
    period: Optional[str]


class DisruptionResponseModel(ResponseModel):
    disruptions: List[Disruption]

    def get_disruption_by_type(self, type: DisruptionType) -> List[Disruption]:
        return [d for d in self.disruptions if d.type == type]


class DisruptionParams(QueryParams):
    isActive: bool
