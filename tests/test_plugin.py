import os
import pickle
import subprocess


def test_addoption(pytestconfig):
    options = pytestconfig.option
    assert "store" in options
    assert "load" in options


def test_store():
    os.system("pytest --store stored_tests test_mock.py")
    with open("stored_tests", 'rb') as f:
        data = pickle.load(f)
        assert data == {'session': {}, 'package': {}, 'module': {}, 'class': {}, 'function': {
            'tests/test_mock.py::test1': {"('fixture1', 'function', 'tests/test_mock.py', None)": 42}},
                        'workers': {'tests/test_mock.py::test1': None}}


def test_store_and_load(request):
    request.addfinalizer(lambda: os.remove('stored_tests'))
    os.system("pytest --store stored_tests test_mock.py")
    stream = os.popen('ls').read()
    assert "stored_tests" in stream.split('\n')

    stream = os.popen("pytest --load stored_tests test_mock.py").read()
    assert "test_mock.py ." in stream
    assert "1 passed" in stream


def test_store_error(request):
    request.addfinalizer(lambda: os.remove('stored_tests'))
    stream = str(subprocess.Popen("pytest --store", shell=True, stderr=subprocess.PIPE).stderr.read())
    assert "pytest: error: argument --store: expected one argument" in stream

    stream = str(subprocess.Popen("pytest --store test_mock.py", shell=True, stdout=subprocess.PIPE).stdout.read())
    assert "FileExistsError: This file already exists" in stream

    os.mknod("stored_tests")
    stream = str(
        subprocess.Popen("pytest --store stored_tests test_mock.py", shell=True, stdout=subprocess.PIPE).stdout.read())
    assert "FileExistsError: This file already exists" in stream


def test_load_error():
    stream = str(subprocess.Popen("pytest --load", shell=True, stderr=subprocess.PIPE).stderr.read())
    assert "pytest: error: argument --load: expected one argument" in stream

    stream = os.popen("pytest --load ferko42").read()
    assert "No such file or directory: 'ferko42'" in stream
