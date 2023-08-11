# airborne-dsa-lite

Data shipping script for airborne products

## Local Development

### Prerequisites

- Python 3 installed
- Python 3 venv installed
- `python3 -m venv env`
- `source env/bin/activate`
- `python3 -m pip install --upgrade pip setuptools pyinstaller`

### Running locally

## Getting started

- `source env/bin/activate`
- `pip3 install .`
- `python3 airborne_dsa/main.py`

## Generating build

- `pyinstaller airborne_dsa/main.py --onefile`
