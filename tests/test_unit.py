import pytest

from pytest_persistence import plugin

plg = plugin.Plugin()


@pytest.mark.parametrize("scope", ["session", "package", "module", "class", "function"])
@pytest.mark.parametrize("result", ["result", 42])
def test_store_fixture(result, scope):
    fixture_id = ('fixture1', scope, 'tests/test_mock.py')
    plg.store_fixture(result, fixture_id, 'tests/test_mock.py', None)
    if scope == "session":
        assert plg.output[scope] == {"('fixture1', 'session', 'tests/test_mock.py', None)": result}
    else:
        assert plg.output[scope]["tests/test_mock.py"] == {
            f"('fixture1', '{scope}', 'tests/test_mock.py', None)": result}


@pytest.fixture(params=[(x, y)
                        for x in ["session", "package", "module", "class", "function"]
                        for y in ["result", 42]])
def store_fixtures(request):
    scope = request.param[0]
    result = request.param[1]
    fixture_id = ('fixture1', scope, 'tests/test_mock.py')
    plg.store_fixture(result, fixture_id, 'tests/test_mock.py', None)
    plg.input = plg.output
    return scope, result


def test_load_fixture(store_fixtures):
    scope = store_fixtures[0]
    result = store_fixtures[1]
    fixture_id = ('fixture1', scope, 'tests/test_mock.py')
    fixture_result = plg.load_fixture(fixture_id, 'tests/test_mock.py')
    assert fixture_result == result
