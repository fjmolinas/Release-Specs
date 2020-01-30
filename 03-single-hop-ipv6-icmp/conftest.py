import pytest
import os

def pytest_addoption(parser):
    parser.addoption(
        "--local", action="store_true", default=False, help="use local boards"
    )

def pytest_collection_modifyitems(config, items):
    if os.geteuid() == 0:
        # user is root, can run sudo tests
        sudo_user = True
    else:
        sudo_user = False
        sudo_only = pytest.mark.skip(reason="test needs sudo to run")

    if config.getoption("--local"):
        # --local given in cli
        run_local = True
    else:
        run_local = False
        local_only = pytest.mark.skip(reason="test cant run on iotlab")

    for item in items:
        if "local_only" in item.keywords and not run_local:
            item.add_marker(local_only)
        if "sudo_only" in item.keywords and not sudo_user:
            item.add_marker(sudo_only)

@pytest.fixture
def local(request):
    return request.config.getoption("--local")
