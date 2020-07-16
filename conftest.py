# pylint: disable=W0613,W0621

"""
Central pytest definitions.

See https://docs.pytest.org/en/stable/fixture.html#conftest-py-sharing-fixture-functions
"""     # noqa: E501

import os
import subprocess
import sys
from collections.abc import Iterable

import pytest
from riotctrl.ctrl import RIOTCtrl

import testutils.pytest
from testutils.iotlab import IoTLABExperiment, DEFAULT_SITE


IOTLAB_EXPERIMENT_DURATION = 120
RIOTBASE = os.environ.get('RIOTBASE')
RUNNING_CTRLS = []
RUNNING_EXPERIMENTS = []


def pytest_addoption(parser):
    """
    register argparse-style options and ini-style config values, called once at
    the beginning of a test run.

    See https://docs.pytest.org/en/stable/reference.html#_pytest.hookspec.pytest_addoption
    """     # noqa: E501
    parser.addoption(
        "--local", action="store_true", default=False, help="use local boards",
    )
    parser.addoption(
        "--hide-output", action="store_true", default=False,
        help="Don't log output of nodes",
    )
    parser.addoption(
        "--boards", type=testutils.pytest.list_from_string,
        help="list of BOARD's or IOTLAB_NODEs for the test",
    )
    parser.addoption(
        "--non-RC", action="store_true", default=False,
        help="Runs test even if RIOT version under test is not an RC",
    )
    parser.addoption(
        "--self-test", action="store_true", default=False,
        help="Tests the testutils rather than running the release tests",
    )


def pytest_ignore_collect(path, config):
    """
    return True to prevent considering this path for collection.

    See: https://docs.pytest.org/en/stable/reference.html#_pytest.hookspec.pytest_ignore_collect
    """     # noqa: E501
    # This is about the --self-test option so I don't agree with pylint here
    # pylint: disable=R1705
    if config.getoption("--self-test"):
        return "testutils" not in str(path)
    else:
        return "testutils" in str(path)


def pytest_collection_modifyitems(config, items):
    # pylint: disable=C0301
    """
    called after collection has been performed, may filter or re-order the
    items in-place.

    See: https://docs.pytest.org/en/stable/reference.html#_pytest.hookspec.pytest_collection_modifyitems
    """     # noqa: E501
    # --local given by CLI
    run_local = config.getoption("--local")
    sudo_only_mark = testutils.pytest.check_sudo()
    local_only_mark = testutils.pytest.check_local(run_local)
    iotlab_creds_mark = testutils.pytest.check_credentials(run_local)
    rc_only_mark = testutils.pytest.check_rc(not config.getoption("--non-RC"))

    for item in items:
        if local_only_mark and "local_only" in item.keywords:
            item.add_marker(local_only_mark)
        if sudo_only_mark and "sudo_only" in item.keywords:
            item.add_marker(sudo_only_mark)
        if iotlab_creds_mark and "iotlab_creds" in item.keywords:
            item.add_marker(iotlab_creds_mark)
        if rc_only_mark and "rc_only" in item.keywords:
            item.add_marker(rc_only_mark)


def pytest_keyboard_interrupt(excinfo):
    # pylint: disable=C0301
    """
    Called on KeyInterrupt

    See: https://docs.pytest.org/en/stable/reference.html?highlight=hooks#_pytest.hookspec.pytest_keyboard_interrupt
    """     # noqa: E501
    for child in RUNNING_CTRLS:
        child.stop_term()
    for exp in RUNNING_EXPERIMENTS:
        exp.stop()


@pytest.fixture
def log_nodes(request):
    """
    Show output of nodes

    :return: True if output of nodes should be shown, False otherwise
    """
    # use reverse, since from outside we most of the time _want_ to log
    return not request.config.getoption("--hide-output")


@pytest.fixture
def local(request):
    """
    Use local boards

    :return: True if local boards should be used, False otherwise
    """
    return request.config.getoption("--local")


@pytest.fixture
def riotbase(request):
    """
    RIOT directory to test. Taken from the variable `RIOTBASE`
    """
    return os.path.abspath(RIOTBASE)


@pytest.fixture
def boards(request):
    """
    String list of boards to use for the test.
    Values are used for the RIOT environment variables `IOTLAB_NODE` or `BOARD`
    """
    return request.config.getoption("--boards")


def get_namefmt(request):
    name_fmt = {}
    if request.module:
        name_fmt["module"] = request.module.__name__.replace("test_", "-")
    if request.function:
        name_fmt["function"] = request.function.__name__ \
                               .replace("test_", "-")
    return name_fmt


@pytest.fixture
def nodes(local, request, boards):
    """
    Provides the nodes for a test as a list of RIOTCtrl objects
    """
    ctrls = []
    if boards is None:
        boards = request.param
    only_native = all(b.startswith("native") for b in boards)
    for board in boards:
        if local or only_native or IoTLABExperiment.valid_board(board):
            env = {'BOARD': '{}'.format(board)}
        else:
            env = {
                'BOARD': IoTLABExperiment.board_from_iotlab_node(board),
                'IOTLAB_NODE': '{}'.format(board)
            }
        ctrls.append(RIOTCtrl(env=env))
    if local or only_native:
        yield ctrls
    else:
        name_fmt = get_namefmt(request)
        # Start IoT-LAB experiment if requested
        exp = IoTLABExperiment(
            name="RIOT-release-test{module}{function}".format(**name_fmt),
            ctrls=ctrls,
            site=os.environ.get("IOTLAB_SITE", DEFAULT_SITE))
        RUNNING_EXPERIMENTS.append(exp)
        exp.start(duration=IOTLAB_EXPERIMENT_DURATION)
        yield ctrls
        exp.stop()
        RUNNING_EXPERIMENTS.remove(exp)


def update_env(node, modules=None, cflags=None, port=None):
    if not isinstance(modules, str) and \
       isinstance(modules, Iterable):
        node.env['USEMODULE'] = ' '.join(str(m) for m in modules)
    elif modules is not None:
        node.env['USEMODULE'] = modules
    if cflags is not None:
        node.env['CFLAGS'] = cflags
    if port is not None:
        node.env['PORT'] = port


@pytest.fixture
def riot_ctrl(log_nodes, nodes, riotbase):
    """
    Factory to create RIOTCtrl objects from list nodes provided by nodes
    fixture
    """
    factory_ctrls = []

    # pylint: disable=R0913
    def ctrl(nodes_idx, application_dir, shell_interaction_cls,
             board_type=None, modules=None, cflags=None, port=None):
        if board_type is not None:
            node = next(n for n in nodes if n.board() == board_type)
        else:
            node = nodes[nodes_idx]
        update_env(node, modules, cflags, port)
        # need to access private member here isn't possible otherwise sadly :(
        # pylint: disable=W0212
        node._application_directory = os.path.join(riotbase, application_dir)
        node.make_run(['flash'], check=True,
                      stdout=None if log_nodes else subprocess.DEVNULL,
                      stderr=None if log_nodes else subprocess.DEVNULL)
        termargs = {}
        if log_nodes:
            termargs["logfile"] = sys.stdout
        RUNNING_CTRLS.append(node)
        node.start_term(**termargs)
        factory_ctrls.append(node)
        return shell_interaction_cls(node)

    yield ctrl

    for node in factory_ctrls:
        try:
            node.stop_term()
            RUNNING_CTRLS.remove(node)
        except RuntimeError:
            # Process had to be forced kill, happens with native
            pass
