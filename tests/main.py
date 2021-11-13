import os.path

from api import NSApi

api = NSApi()


def test_stations() -> None:
    stations = api.get_stations().stations
    assert len(stations) > 550
    assert os.path.exists("data/stations.json")


def test_station_name_resolve() -> None:
    leiden = api.resolve_station_name("Leiden Centraal")
    assert leiden is not None
    assert leiden.code == "LEDN"


def test_delay() -> None:
    route_delays = api.get_delay_info("UT", "AMS")
    assert len(route_delays) > 0
