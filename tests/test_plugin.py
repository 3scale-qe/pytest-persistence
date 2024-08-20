import os
import pickle
import subprocess


def test_addoption(pytestconfig):
    options = pytestconfig.option
    assert "store" in options
    assert "load" in options


def test_no_persistence():
    os.system("pytest tests/test_mock.py")

    assert not os.path.exists("tmp")


def test_store():
    os.system("pytest --store stored_tests tests/test_mock.py")
    with open("stored_tests", 'rb') as f:
        data = pickle.load(f)
        assert data == {
            'class': {},
            'function': {'tests/test_mock.py::test1': {"('fixture1', 'function', 'tests/test_mock.py', None)": 42},
                         'tests/test_mock.py::test2': {"('fixture2', 'function', 'tests/test_mock.py', None)": 'tmp'}},
            'module': {},
            'package': {},
            'session': {"('cleanup', 'session', 'tests/test_mock.py', None)": True},
            'tests': {'tests/test_mock.py::test1': None,
                      'tests/test_mock.py::test2': None},
            'workers': {'tests/test_mock.py::test1': None,
                         'tests/test_mock.py::test2': None}}

        assert os.path.isdir("tmp")


def test_store_and_load(request):
    request.addfinalizer(lambda: os.remove('stored_tests'))
    os.system("pytest --store stored_tests tests/test_mock.py")
    stream = os.popen('ls').read()
    assert "stored_tests" in stream.split('\n')

    assert os.path.isdir("tmp")

    stream = os.popen("pytest --load stored_tests tests/test_mock.py").read()
    assert "test_mock.py ." in stream
    assert "2 passed" in stream

    assert os.path.isdir("tmp")


def test_store_error(request):
    request.addfinalizer(lambda: os.remove('stored_tests'))
    stream = str(subprocess.Popen("pytest --store", shell=True, stderr=subprocess.PIPE).stderr.read())
    assert "pytest: error: argument --store: expected one argument" in stream

    stream = str(subprocess.Popen("pytest --store tests/test_mock.py", shell=True, stdout=subprocess.PIPE).stdout.read())
    assert "FileExistsError: This file already exists" in stream

    os.mknod("stored_tests")
    stream = str(
        subprocess.Popen("pytest --store stored_tests tests/test_mock.py", shell=True, stdout=subprocess.PIPE).stdout.read())
    assert "FileExistsError: This file already exists" in stream


def test_load_error():
    stream = str(subprocess.Popen("pytest --load", shell=True, stderr=subprocess.PIPE).stderr.read())
    assert "pytest: error: argument --load: expected one argument" in stream

    stream = os.popen("pytest --load ferko42").read()
    assert "No such file or directory: 'ferko42'" in stream


def test_bug(request):
    request.addfinalizer(lambda: os.remove('stored_tests'))
    os.system("pytest --store stored_tests tests/mock/")
    stream = os.popen('ls').read()
    assert "stored_tests" in stream.split('\n')

    stream = os.popen("pytest --load stored_tests tests/mock").read()
    assert "tests/mock/test_A.py . " in stream
    assert "tests/mock/test_B.py . " in stream
    assert "2 passed" in stream

