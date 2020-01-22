import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--local", action="store_true", default=False, help="use local boards"
    )

def pytest_collection_modifyitems(config, items):
    if config.getoption("--local"):
        # --local given in cli: all tests can run
        return
    local_only = pytest.mark.skip(reason="test cant run on iotlab")
    for item in items:
        if "local_only" in item.keywords:
            item.add_marker(local_only)

@pytest.fixture
def local(request):
    return request.config.getoption("--local")
