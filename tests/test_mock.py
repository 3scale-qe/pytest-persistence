import pytest


@pytest.fixture
def fixture1():
    return 42


def test1(fixture1):
    assert fixture1 == 42
