import click

from api import NSApi


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
    api.get_stations()


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
    cli.add_command(stations)
    cli()
