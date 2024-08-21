import pytest


@pytest.fixture(scope='module')
def fnc(fnc):
    fnc.append("A")
    return fnc


def test_A(fnc):
    assert fnc == ["A"]
