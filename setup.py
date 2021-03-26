"""This module makes the pytest_persistence plugin pip installable."""
from setuptools import setup

from pytest_persistence import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

extra_requirements = {
    'dev': [
        'pytest'
    ]
}

setup(name="pytest-persistence",
      version=__version__,
      description="Pytest tool for persistent objects",
      author="Jakub Urban",
      author_email="kubo.urban@gmail.com",
      maintainer="Jakub Urban",
      url="https://github.com/JaurbanRH/pytest-persistence",
      packages=["pytest_persistence"],
      long_description=long_description,
      entry_points={
          "pytest11": ["persistence = pytest_persistence.plugin"]
      },
      classifiers=[
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.7",
          "Operating System :: OS Independent",
          "License :: OSI Approved :: MIT License",
      ],
      )
