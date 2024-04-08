# pytest-persistence

Pytest plugin for persistent fixtures.

## Installation

In a Python environment do:

    python -m pip install pytest-persistence

## Usage

To store fixtures to file run tests with `--store {file_path}`:

    python -m pytest --store {file_path}

To load fixtures from file run tests with `--load {file_path}`:

    python -m pytest --load {file_path}

**BEWARE** When this plugin is in use cleanup of all the fixtures is **not**
executed. This is necessary to successfully run tests with `--load`. However it
is important to keep this fact in mind.
