import click

from api import NSApi
from models.disruptions import DisruptionType


@click.group()
def cli() -> None:
    pass


@click.command()
@click.option(
    "--station", default="UT", help="Station to get departure information of."
)
def main(station: str) -> None:
    """Returns route information from the NS API"""
    api = NSApi()
    for dep in api.get_departure_info(station).departures:
        print(dep)


@click.command()
def stations() -> None:
    """Fetches stations from the NS API"""
    api = NSApi()
    stations_data = api.get_stations().stations
    print(f"Received {len(stations_data)} stations")


@click.command()
def disruptions() -> None:
    """Fetches stations from the NS API"""
    api = NSApi()
    data = api.get_disruptions()

    maintenance_count = len(data.get_disruption_by_type(DisruptionType.MAINTENANCE))
    disruption_count = len(data.get_disruption_by_type(DisruptionType.DISRUPTION))
    calamity_count = len(data.get_disruption_by_type(DisruptionType.CALAMITY))

    print(f"Found {maintenance_count} maintenances")
    print(f"Found {disruption_count} disruptions")
    print(f"Found {calamity_count} calamities")


@click.command()
@click.option("--origin", default="UT", help="Origin of route to get delay of.")
@click.option(
    "--destination", default="LEDN", help="Destination of route to get delay of."
)
@click.option(
    "--short/--long",
    default=False,
    help="Short format only returns delay (in seconds) for the next departure.",
)
def delay(origin: str, destination: str, short: bool) -> None:
    """Returns route delay from the NS API"""
    api = NSApi()
    route_delays = api.get_delay_info(origin, destination)

    if short:
        print(route_delays[0].delay.total_seconds())
        return

    for route_delay in route_delays:
        print(route_delay)


if __name__ == "__main__":
    cli.add_command(main)
    cli.add_command(delay)
    cli.add_command(disruptions)
    cli.add_command(stations)
    cli()
