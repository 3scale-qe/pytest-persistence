import pytest
import os


@pytest.fixture(scope="session", autouse=True)
def cleanup():
    if os.path.isdir("tmp"):
        os.rmdir("tmp")
    return True


@pytest.fixture
def fixture1():
    return 42


def test1(fixture1):
    assert fixture1 == 42

@pytest.fixture()
def fixture2(request):
    request.addfinalizer(lambda: os.rmdir("tmp"))
    os.mkdir("tmp")
    return "tmp"

def test2(fixture2):
    assert os.path.exists("tmp")
