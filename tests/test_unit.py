import pytest

from pytest_persistence import plugin


@pytest.mark.parametrize("scope", ["session", "package", "module", "class", "function"])
@pytest.mark.parametrize("result", ["result", 42])
def test_store_fixture(result, scope):
    plugin.store_fixture(result, scope, "test_fixture", "file")
    if scope == "session":
        assert plugin.OUTPUT[scope] == {"test_fixture": result}
    else:
        assert plugin.OUTPUT[scope]["file"] == {"test_fixture": result}


@pytest.fixture(params=[(x, y)
                        for x in ["session", "package", "module", "class", "function"]
                        for y in ["result", 42]])
def store_fixtures(request):
    scope = request.param[0]
    result = request.param[1]
    plugin.store_fixture(result, scope, "test_fixture", "file")
    plugin.INPUT = plugin.OUTPUT
    return scope, result


def test_load_fixture(store_fixtures):
    scope = store_fixtures[0]
    result = store_fixtures[1]
    fixture_result = plugin.load_fixture(scope, "test_fixture", "file")
    assert fixture_result == result


@pytest.mark.parametrize(("scope", "result"), [("package", "tests"), ("module", "test_unit.py"), ("class", None),
                                               ("function", "tests/test_unit.py:test_set_scope_file[function]")],
                         ids=["package", "module", "class", "function"])
def test_set_scope_file(scope, result, request):
    file = request._pyfuncitem.location[0]
    scope_file = plugin.set_scope_file(scope, file, request)
    assert scope_file == result
