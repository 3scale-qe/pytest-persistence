import pickle

TMP = {}
DATA = {}


def pytest_addoption(parser):
    parser.addoption(
        "--store", action="store", default=False, help="Store config")
    parser.addoption(
        "--load", action="store", default=False, help="Load config")


def pytest_sessionstart(session):
    if file := session.config.getoption("--load"):
        with open(file, 'rb') as f:
            global DATA
            DATA = pickle.load(f)


def pytest_sessionfinish(session):
    if file := session.config.getoption("--store"):
        with open(file, 'wb') as outfile:
            pickle.dump(TMP, outfile)


def pytest_fixture_setup(fixturedef, request):
    kwargs = {}
    my_cache_key = fixturedef.cache_key(request)
    file_name = request._pyfuncitem.location[0]
    test_name = request._pyfuncitem.name

    if request.config.getoption("--load"):
        if fixturevalue := DATA.get(file_name).get(test_name).get(fixturedef.argname):
            fixturedef.cached_result = (fixturevalue, my_cache_key, None)
            return fixturevalue

    for argname in fixturedef.argnames:
        fixdef = request._get_active_fixturedef(argname)
        assert fixdef.cached_result is not None
        result, arg_cache_key, exc = fixdef.cached_result
        request._check_scope(argname, request.scope, fixdef.scope)
        kwargs[argname] = result

    if kwargs:
        result = fixturedef.func(**kwargs)
    else:
        result = fixturedef.func()

    if request.config.getoption("--store"):
        try:
            pickle.dumps(result)
            if TMP.get(file_name):
                if TMP[file_name].get(test_name):
                    TMP[file_name][test_name].update({fixturedef.argname: result})
                else:
                    TMP[file_name].update({test_name: {fixturedef.argname: result}})
            else:
                TMP.update({file_name: {test_name: {fixturedef.argname: result}}})
        except:
            pass

    fixturedef.cached_result = (result, my_cache_key, None)
    return result
