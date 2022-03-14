import pytest

from pytest_persistence import plugin

plg = plugin.Plugin()


@pytest.mark.parametrize("scope", ["session", "package", "module", "class", "function"])
@pytest.mark.parametrize("result", ["result", 42])
def test_store_fixture(result, scope):
    plg.store_fixture(result, scope, "test_fixture", "file")
    if scope == "session":
        assert plg.output[scope] == {"test_fixture": result}
    else:
        assert plg.output[scope]["file"] == {"test_fixture": result}


@pytest.fixture(params=[(x, y)
                        for x in ["session", "package", "module", "class", "function"]
                        for y in ["result", 42]])
def store_fixtures(request):
    scope = request.param[0]
    result = request.param[1]
    plg.store_fixture(result, scope, "test_fixture", "file")
    plg.input = plg.output
    return scope, result


def test_load_fixture(store_fixtures):
    scope = store_fixtures[0]
    result = store_fixtures[1]
    fixture_result = plg.load_fixture(scope, "test_fixture", "file")
    assert fixture_result == result
