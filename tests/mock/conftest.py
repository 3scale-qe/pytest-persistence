import pytest


@pytest.fixture(scope='module')
def fnc(request):
    class _Tmp:
        def create_list(self):
            return []

    return _Tmp().create_list()
