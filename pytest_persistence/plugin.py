import pickle

from _pytest.fixtures import pytest_fixture_setup as fixture_result

OUTPUT = {"session": {}, "package": {}, "module": {}, "class": {}, "function": {}}
INPUT = {}


def pytest_addoption(parser):
    """
    Add option to store/load fixture results into file
    """
    parser.addoption(
        "--store", action="store", default=False, help="Store config")
    parser.addoption(
        "--load", action="store", default=False, help="Load config")


def pytest_sessionstart(session):
    """
    Called after the ``Session`` object has been created and before performing collection
    and entering the run test loop. Checks whether '--load' switch is present. If it is, load
    fixtures results from given file.
    """
    if file := session.config.getoption("--load"):
        with open(file, 'rb') as f:
            global INPUT
            INPUT = pickle.load(f)


def pytest_sessionfinish(session):
    """
    Called after whole test run finished, right before returning the exit status to the system.
    Checks whether '--store' switch is present. If it is, store fixtures results to given file.
    """
    if file := session.config.getoption("--store"):
        with open(file, 'wb') as outfile:
            pickle.dump(OUTPUT, outfile)


def pytest_fixture_setup(fixturedef, request):
    """
    Perform fixture setup execution.
    If '--load' switch is present, tries to find fixture results in stored results.
    If '--store' switch is present, store fixture result.
    :returns: The return value of the fixture function.
    """
    my_cache_key = fixturedef.cache_key(request)
    fixture_name = fixturedef.argname
    scope = fixturedef.scope
    file_name = request._pyfuncitem.location[0]
    if scope == "package":
        scope_file = file_name.rsplit("/", 1)[0]
    elif scope == "module":
        scope_file = file_name.rsplit("/", 1)[1]
    elif scope == "class":
        scope_file = request._pyfuncitem.cls
    elif scope == "function":
        scope_file = f"{file_name}:{request._pyfuncitem.name}"

    if request.config.getoption("--load"):
        if scope == "session":
            if result := INPUT[scope].get(fixture_name):
                fixturedef.cached_result = (result, my_cache_key, None)
                return result
        else:
            if result := INPUT[scope].get(scope_file).get(fixture_name):
                fixturedef.cached_result = (result, my_cache_key, None)
                return result

    result = fixture_result(fixturedef, request)

    if request.config.getoption("--store"):
        try:
            pickle.dumps(result)
            if scope == "session":
                OUTPUT[scope].update({fixture_name: result})
            else:
                if OUTPUT[scope].get(scope_file):
                    OUTPUT[scope][scope_file].update({fixture_name: result})
                else:
                    OUTPUT[scope].update({scope_file: {fixture_name: result}})
        except:
            pass

    return result
