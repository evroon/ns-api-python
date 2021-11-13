from dataclasses import dataclass


@dataclass
class StationNotFoundException(Exception):
    station_name: str
