import os.path

from api import NSApi
from models.disruptions import DisruptionType

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
    api.get_delay_info("UT", "ASD")


def test_disruptions() -> None:
    disruptions = api.get_disruptions()
    assert len(disruptions.disruptions) > 0

    maintenance_count = len(
        disruptions.get_disruption_by_type(DisruptionType.MAINTENANCE)
    )
    disruption_count = len(
        disruptions.get_disruption_by_type(DisruptionType.DISRUPTION)
    )
    calamity_count = len(disruptions.get_disruption_by_type(DisruptionType.CALAMITY))

    assert maintenance_count + disruption_count + calamity_count == len(
        disruptions.disruptions
    )
