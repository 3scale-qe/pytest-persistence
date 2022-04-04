import os
import pickle
from pprint import pformat

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
        and entering the run test loop. Checks whether '--load' option is present. If it is, load
        fixtures results from given file.
        """
        if file := session.config.getoption("--store"):
            if os.path.isfile(file):
                raise FileExistsError("This file already exists")
        if file := session.config.getoption("--load"):
            with open(file, 'rb') as f:
                self.input = pickle.load(f)

    def check_output(self):
        """Check if output dict can be serialized"""

        def check_fixtures(fixtures):
            to_remove = []
            for k, v in fixtures.items():
                try:
                    pickle.dumps(v)
                except Exception:
                    to_remove.append(k)
            for fixture in to_remove:
                fixtures.pop(fixture)
                if fixture in self.pickled_fixtures:
                    self.pickled_fixtures.remove(fixture)
                    self.unable_to_pickle.add(fixture)

        for scope, fixtures in self.output.items():
            if scope == "session":
                check_fixtures(fixtures)
            else:
                for key, value in fixtures.items():
                    check_fixtures(value)

    def output_to_file(self, filename):
        """Serialize output dict into file"""
        with open(filename, 'wb') as outfile:
            self.check_output()
            pickle.dump(self.output, outfile)

    def merge_dicts(self, fixtures):
        for k, v in fixtures.items():
            self.output[k].update(v)

    def pytest_sessionfinish(self, session):
        """
        Called after whole test run finished, right before returning the exit status to the system.
        Checks whether '--store' option is present. If it is, store fixtures results to given file.
        """
        if file := session.config.getoption("--store"):
            if worker := os.getenv("PYTEST_XDIST_WORKER"):
                self.output_to_file(f"{file}_{worker}")
                print(f"\nStored fixtures:\n{pformat(self.pickled_fixtures)}")
                print(f"\nUnstored fixtures:\n{pformat(self.unable_to_pickle)}")
                return
            if workers := session.config.getoption("-n"):
                for i in range(workers):
                    with open(f"{file}_gw{i}", 'rb') as f:
                        self.merge_dicts(pickle.load(f))
                        os.remove(f"{file}_gw{i}")
            self.output_to_file(file)
            print(f"\nStored fixtures:\n{pformat(self.pickled_fixtures)}")
            print(f"\nUnstored fixtures:\n{pformat(self.unable_to_pickle)}")

    def load_fixture(self, scope, fixture_id, node_id):
        """
        Load fixture result
        """
        if scope == "session":
            if result := self.input[scope].get(fixture_id):
                return result
        else:
            if result := self.input[scope].get(node_id).get(fixture_id):
                return result

    def store_fixture(self, result, scope, fixture_id, node_id):
        """
        Store fixture result
        """
        if scope == "session":
            self.output[scope].update({fixture_id: result})
        else:
            if self.output[scope].get(node_id):
                self.output[scope][node_id].update({fixture_id: result})
            else:
                self.output[scope].update({node_id: {fixture_id: result}})

    def pytest_fixture_setup(self, fixturedef, request):
        """
        Perform fixture setup execution.
        If '--load' switch is present, tries to find fixture results in stored results.
        If '--store' switch is present, store fixture result.
        :returns: The return value of the fixture function.
        """
        my_cache_key = fixturedef.cache_key(request)
        fixture_id = str(fixturedef)
        scope = fixturedef.scope
        node_id = request._pyfuncitem._nodeid

        if request.config.getoption("--load"):
            result = self.load_fixture(scope, fixture_id, node_id)
            if result:
                fixturedef.cached_result = (result, my_cache_key, None)
                return result
        result = fixture_result(fixturedef, request)

        if request.config.getoption("--store"):
            try:
                pickle.dumps(result)
                self.pickled_fixtures.add(fixture_id)
                self.store_fixture(result, scope, fixture_id, node_id)
            except Exception:
                self.unable_to_pickle.add(fixture_id)

        return result


def pytest_configure(config):
    """
    Hook ensures that plugin works only when the --load or --store option is present.
    """
    if config.getoption("--load") or config.getoption("--store"):
        config.pluginmanager.register(Plugin())
