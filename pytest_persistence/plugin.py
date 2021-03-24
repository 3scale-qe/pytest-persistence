import pickle
import sys

from _pytest.fixtures import resolve_fixture_function, call_fixture_func
from _pytest.outcomes import TEST_OUTCOME

OUTPUT = {}
INPUT = {}


def pytest_addoption(parser):
    parser.addoption(
        "--store", action="store", default=False, help="Store config")
    parser.addoption(
        "--load", action="store", default=False, help="Load config")


def pytest_sessionstart(session):
    if file := session.config.getoption("--load"):
        with open(file, 'rb') as f:
            global INPUT
            INPUT = pickle.load(f)


def pytest_sessionfinish(session):
    if file := session.config.getoption("--store"):
        with open(file, 'wb') as outfile:
            pickle.dump(OUTPUT, outfile)


def pytest_fixture_setup(fixturedef, request):
    kwargs = {}
    my_cache_key = fixturedef.cache_key(request)
    file_name = request._pyfuncitem.location[0]
    test_name = request._pyfuncitem.name

    if request.config.getoption("--load"):
        if fixturevalue := INPUT.get(file_name).get(test_name).get(fixturedef.argname):
            fixturedef.cached_result = (fixturevalue, my_cache_key, None)
            return fixturevalue

    for argname in fixturedef.argnames:
        fixdef = request._get_active_fixturedef(argname)
        assert fixdef.cached_result is not None
        result, arg_cache_key, exc = fixdef.cached_result
        request._check_scope(argname, request.scope, fixdef.scope)
        kwargs[argname] = result

    fixturefunc = resolve_fixture_function(fixturedef, request)
    my_cache_key = fixturedef.cache_key(request)
    try:
        result = call_fixture_func(fixturefunc, request, kwargs)
    except TEST_OUTCOME:
        exc_info = sys.exc_info()
        assert exc_info[0] is not None
        fixturedef.cached_result = (None, my_cache_key, exc_info)
        raise

    if request.config.getoption("--store"):
        try:
            pickle.dumps(result)
            if OUTPUT.get(file_name):
                if OUTPUT[file_name].get(test_name):
                    OUTPUT[file_name][test_name].update({fixturedef.argname: result})
                else:
                    OUTPUT[file_name].update({test_name: {fixturedef.argname: result}})
            else:
                OUTPUT.update({file_name: {test_name: {fixturedef.argname: result}}})
        except:
            pass

    fixturedef.cached_result = (result, my_cache_key, None)
    return result
