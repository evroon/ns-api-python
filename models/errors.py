from dataclasses import dataclass


@dataclass
class StationNotFoundException(Exception):
    station_name: str


@dataclass()
class NSApiException(Exception):
    statusCode: int
    message: str

    def __str__(self) -> str:
        return f"{self.statusCode} - {self.message}"
