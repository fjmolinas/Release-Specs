import os
import pytest

# If no path is given use RIOTBASE environment variable
RIOTBASE = os.environ.get('RIOTBASE', None)


def list_from_string(list_str=None):
    """Get list of items from `list_str`

    >>> list_from_string(None)
    []
    >>> list_from_string("")
    []
    >>> list_from_string("  ")
    []
    >>> list_from_string("a")
    ['a']
    >>> list_from_string("a  ")
    ['a']
    >>> list_from_string("a b  c")
    ['a', 'b', 'c']
    """
    value = (list_str or '').split(' ')
    return [v for v in value if v]


def pytest_addoption(parser):
    parser.addoption(
        "--local", action="store_true", default=False, help="use local boards",
    )
    parser.addoption(
        "--riotbase", default=RIOTBASE, help="RIOTBASE dir",
    )
    parser.addoption(
        "--boards", type=list_from_string,
        help="list of BOARD's or IOTLAB_NODEs for the test",
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


@pytest.fixture
def riotbase(request):
    return os.path.abspath(request.config.getoption("--riotbase"))


@pytest.fixture
def boards(request):
    return request.config.getoption("--boards")
