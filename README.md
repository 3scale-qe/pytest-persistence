# pytest-persistence

Pytest tool for persistent objects

## Installation

In a Python environment do:

    python -m pip install pytest-persistence

## Usage

To store fixtures to file run tests with `--store {file_path}`:

    python -m pytest --store {file_path}

To load fixtures from file run tests with `--load {file_path}`:

    python -m pytest --load {file_path}
