# Python NS API


[![mypy](https://github.com/evroon/ns-api-python/actions/workflows/mypy.yml/badge.svg)](https://github.com/evroon/ns-api-python/actions/workflows/mypy.yml)

This project serves as a simple Python client of the [NS API](https://apiportal.ns.nl).
The reponses are stored in Pydantic models, enabling easy manipulation and validation of the data.

## Setup
Get a (free) API key from NS (see the [startersguide](https://apiportal.ns.nl/startersguide)).

Create a file called `.env` with the following content: (see `sample.env`)
```bash
API_KEY="<api key>"
```

## Usage
Run `python3 main.py --help` to see a list of commands.

It is recommended to first run `python3 main.py stations` to retrieve (and store) a list of all stations.
