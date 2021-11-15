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
from models.disruptions import DisruptionResponseModel, DisruptionParams
from models.errors import StationNotFoundException, NSApiException
from models.stations import StationResponseModel, Station

load_dotenv()


class NSApi:
    data_dir = "data"
    station_info_path = f"{data_dir}/stations.json"
    base_url = "https://gateway.apiportal.ns.nl/reisinformatie-api/api/"

    @staticmethod
    def create_dir(dir: str) -> None:
        if not os.path.exists(dir):
            os.makedirs(dir)

    def send_request(
        self,
        endpoint: str,
        params: QueryParams = QueryParams(),
        response_model: Type[ResponseModel] = ResponseModel,
        root_key: Optional[str] = None,
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
        if root_key is not None:
            response_json = {root_key: response_json}

        try:
            result = response_model(**response_json)
        except ValidationError as e:
            if "statusCode" in response_json:
                raise NSApiException(**response_json)
            else:
                raise e

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
        response = self.send_request("v2/stations", response_model=StationResponseModel)
        assert isinstance(response, StationResponseModel)

        self.save_json(self.station_info_path, response)
        return response

    def get_disruptions(self) -> DisruptionResponseModel:
        response = self.send_request(
            "v3/disruptions",
            response_model=DisruptionResponseModel,
            root_key="disruptions",
            params=DisruptionParams(isActive=True),
        )
        assert isinstance(response, DisruptionResponseModel)
        return response

    def get_departure_info(self, station_name: str) -> DeparturePayloadModel:
        station = self.resolve_station_name(station_name)
        if station is None:
            raise StationNotFoundException(station_name=station_name)

        response = self.send_request(
            "v2/departures",
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
        self, origin_name: str, destination_name: Optional[str] = None
    ) -> List[DelayInfo]:
        departures = self.get_departure_info(origin_name).departures
        result: List[DelayInfo] = []
        destination = None

        if destination_name is not None:
            destination = self.resolve_station_name(destination_name)
            assert destination is not None

        def is_match(dep: Departure) -> bool:
            assert destination is not None
            return dep.direction == destination.names.long

        for departure in departures:
            assert isinstance(departure, Departure)
            if destination_name is None or is_match(departure):
                assert departure.delay is not None
                already_in_result = False

                # Check if the same route already exists in the result list; if so: skip it.
                for x in result:
                    if (
                        x.origin == departure.delay.origin
                        and x.destination == departure.delay.destination
                    ):
                        already_in_result = True
                        break

                if not already_in_result:
                    result.append(departure.delay)

        return result
