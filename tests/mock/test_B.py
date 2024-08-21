import pytest


@pytest.fixture(scope='module')
def fnc(fnc):
    fnc.append("B")
    return fnc


def test_B(fnc):
    assert fnc == ["B"]
