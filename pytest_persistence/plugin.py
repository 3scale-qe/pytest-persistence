import os
import pickle

from _pytest.fixtures import pytest_fixture_setup as fixture_result


def pytest_addoption(parser):
    """
    Add option to store/load fixture results into file
    """
    parser.addoption(
        "--store", action="store", default=False, help="Store config")
    parser.addoption(
        "--load", action="store", default=False, help="Load config")


class Plugin:
    """
    Pytest persistence plugin
    """
    output = {"session": {}, "package": {}, "module": {}, "class": {}, "function": {}}
    input = {}
    unable_to_pickle = set()
    pickled_fixtures = set()

    def pytest_sessionstart(self, session):
        """
        Called after the ``Session`` object has been created and before performing collection
        and entering the run test loop. Checks whether '--load' switch is present. If it is, load
        fixtures results from given file.
        """
        if file := session.config.getoption("--store"):
            if os.path.isfile(file):
                raise FileExistsError("This file already exists")
        if file := session.config.getoption("--load"):
            with open(file, 'rb') as f:
                self.input = pickle.load(f)

    def pytest_sessionfinish(self, session):
        """
        Called after whole test run finished, right before returning the exit status to the system.
        Checks whether '--store' switch is present. If it is, store fixtures results to given file.
        """
        if file := session.config.getoption("--store"):
            with open(file, 'wb') as outfile:
                pickle.dump(self.output, outfile)
        if self.pickled_fixtures:
            print(f"\nStored fixtures: {self.pickled_fixtures}")
        if self.unable_to_pickle:
            print(f"\nUnstored fixtures: {self.unable_to_pickle}")

    def set_scope_file(self, scope, file_name, request):
        """
        Return file_name based on scope of fixture
        """
        if scope == "package":
            return file_name.rsplit("/", 1)[0]
        elif scope == "module":
            return file_name.rsplit("/", 1)[1]
        elif scope == "class":
            return request._pyfuncitem.cls
        elif scope == "function":
            return f"{file_name}:{request._pyfuncitem.name}"

    def load_fixture(self, scope, fixture_name, scope_file):
        """
        Load fixture result
        """
        if scope == "session":
            if result := self.input[scope].get(fixture_name):
                return result
        else:
            if result := self.input[scope].get(scope_file).get(fixture_name):
                return result

    def store_fixture(self, result, scope, fixture_name, scope_file):
        """
        Store fixture result
        """
        if scope == "session":
            self.output[scope].update({fixture_name: result})
        else:
            if self.output[scope].get(scope_file):
                self.output[scope][scope_file].update({fixture_name: result})
            else:
                self.output[scope].update({scope_file: {fixture_name: result}})

    def pytest_fixture_setup(self, fixturedef, request):
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
        scope_file = self.set_scope_file(scope, file_name, request)

        if request.config.getoption("--load"):
            result = self.load_fixture(scope, fixture_name, scope_file)
            if result:
                fixturedef.cached_result = (result, my_cache_key, None)
                return result
        result = fixture_result(fixturedef, request)

        if request.config.getoption("--store"):
            try:
                pickle.dumps(result)
                self.pickled_fixtures.add(fixture_name)
                self.store_fixture(result, scope, fixture_name, scope_file)
            except Exception:
                self.unable_to_pickle.add(fixture_name)

        return result


def pytest_configure(config):
    """
    Hook ensures that plugin works only when the --load or --store option is present.
    """
    if config.getoption("--load") or config.getoption("--store"):
        config.pluginmanager.register(Plugin())
