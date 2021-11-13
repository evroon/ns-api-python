import os
from typing import Type, Optional, List

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

from models.departures import (
    DepartureParams,
    QueryParams,
    ResponseModel,
    DepartureResponseModel,
    DeparturePayloadModel,
    Departure,
    DelayInfo,
)
from models.errors import StationNotFoundException, NSApiException
from models.stations import StationResponseModel, Station

load_dotenv()


class NSApi:
    data_dir = "data"
    station_info_path = f"{data_dir}/stations.json"
    base_url = "https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/"

    @staticmethod
    def create_dir(dir: str) -> None:
        if not os.path.exists(dir):
            os.makedirs(dir)

    def send_request(
        self,
        endpoint: str,
        params: QueryParams = QueryParams(),
        response_model: Type[ResponseModel] = ResponseModel,
    ) -> ResponseModel:
        api_key = os.environ["API_KEY"]
        assert len(api_key) == 32
        headers = {
            "Ocp-Apim-Subscription-Key": api_key,
        }

        response = requests.get(
            self.base_url + endpoint, headers=headers, params=params
        )
        response_json = response.json()

        try:
            result = response_model(**response_json)
        except ValidationError:
            raise NSApiException(**response_json)

        return result

    @staticmethod
    def get_json(model: BaseModel) -> str:
        return model.json(indent=4, sort_keys=True)

    def save_json(self, out_path: str, model: BaseModel) -> None:
        self.create_dir(os.path.dirname(out_path))

        with open(out_path, "w") as f:
            f.write(self.get_json(model))

    def has_station_info(self) -> bool:
        return os.path.exists(self.station_info_path)

    def resolve_station_name(self, name: str) -> Optional[Station]:
        if not self.has_station_info():
            return None

        payload = StationResponseModel.parse_file(
            self.station_info_path,
        )
        for station in payload.stations:
            if station.has_name(name):
                return station

        print(f"Could not find station: {name}")
        return None

    def get_stations(self) -> StationResponseModel:
        response = self.send_request("stations", response_model=StationResponseModel)
        assert isinstance(response, StationResponseModel)

        self.save_json(self.station_info_path, response)
        return response

    def get_departure_info(self, station_name: str) -> DeparturePayloadModel:
        station = self.resolve_station_name(station_name)
        if station is None:
            raise StationNotFoundException(station_name=station_name)

        response = self.send_request(
            "departures",
            DepartureParams(station=station.code),
            response_model=DepartureResponseModel,
        )

        assert isinstance(response, DepartureResponseModel)
        departures = response.payload.departures

        for dep in departures:
            dep.delay = DelayInfo(
                delay=dep.actualDateTime - dep.plannedDateTime,
                origin=station,
                destination=self.resolve_station_name(dep.direction),
                planned_departure=dep.plannedDateTime,
                actual_departure=dep.actualDateTime,
            )

        return response.payload

    def get_delay_info(
        self, origin_name: str, destination_name: Optional[str]
    ) -> List[DelayInfo]:
        departures = self.get_departure_info(origin_name).departures
        result = []

        if destination_name is not None:
            destination = self.resolve_station_name(destination_name)

        for x in departures:
            assert isinstance(x, Departure)
            if destination is None or x.direction == destination.names.long:
                assert x.delay is not None
                result.append(x.delay)

        return result
