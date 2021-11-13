from typing import List

from pydantic import BaseModel, Field

from models.base import ResponseModel


class StationNames(BaseModel):
    long: str = Field(alias='lang')
    medium: str = Field(alias='middel')
    short: str = Field(alias='kort')

    def get_names(self) -> List[str]:
        return [self.long, self.medium, self.short]


    class Config:
        allow_population_by_field_name = True


class Station(BaseModel):
    UICCode: str
    stationType: str
    EVACode: str
    code: str
    land: str
    lat: float
    lng: float
    names: StationNames = Field(alias='namen')
    ingangsDatum: str
    heeftFaciliteiten: bool
    heeftVertrektijden: bool
    heeftReisassistentie: bool

    def has_name(self, name: str) -> bool:
        return name in self.names.get_names() + [self.code]

    class Config:
        allow_population_by_field_name = True


class StationResponseModel(ResponseModel):
    stations: List[Station] = Field(alias='payload')

    class Config:
        allow_population_by_field_name = True
