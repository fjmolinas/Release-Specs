import os
import time
import pytest

from common import udp_send
from testutils.mixins import RIOTNodeShellIfconfig
from testutils.mixins import RIOTNodeShellPktbuf
from testutils.mixins import RIOTNodeShellUdp
from testutils.iotlab import IOTLABNode, IoTLABExperiment


DEVNULL = open(os.devnull, 'w')
IOTLAB_EXPERIMENT_DURATION = 120


class SixLoWPANShell(RIOTNodeShellIfconfig,
                     RIOTNodeShellPktbuf,
                     RIOTNodeShellUdp):
    pass


@pytest.fixture
def nodes(local, request, boards):
    nodes = []
    boards_input = boards if boards else request.param
    for board in boards_input:
        if IoTLABExperiment.valid_board(board):
            env = {'BOARD': '{}'.format(board)}
        else:
            env = {'IOTLAB_NODE': '{}'.format(board)}
        nodes.append(IOTLABNode(env=env))
    if local is True:
        yield nodes
    else:
        exp = IoTLABExperiment(name="RIOT-release-test-06", nodes=nodes)
        exp.start(duration=IOTLAB_EXPERIMENT_DURATION)
        yield nodes
        exp.stop()


@pytest.fixture
def RIOTNode_factory(nodes, riotbase):
    def gnrc_node(i, board_type=None, application_dir="tests/gnrc_udp",
                  modules='gnrc_pktbuf_cmd', cflags=None, port=None):
        if board_type is not None:
            node = next(n for n in nodes if n.board() == board_type)
        else:
            node = nodes[i]
        node.env['USEMODULE'] = modules
        if cflags is not None:
            node.env['CFLAGS'] = cflags
        if port is not None:
            node.env['PORT'] = port
        node._application_directory = os.path.join(riotbase, application_dir)
        node.make_run(['flash'], stdout=DEVNULL, stderr=DEVNULL)
        # Some boards need a delay to start
        time.sleep(3)
        node.start_term()
        return SixLoWPANShell(node)

    yield gnrc_node

    for node in nodes:
        node.stop_term()


@pytest.mark.parametrize('nodes',
                         [pytest.param(['iotlab-m3', 'iotlab-m3'])],
                         indirect=['nodes'])
def test_task01(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0), RIOTNode_factory(1)]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = udp_send(
                                                nodes[i],
                                                nodes[i ^ 1],
                                                nodes[i ^ 1].get_ip_addr(),
                                                port=1337,
                                                count=1000,
                                                payload_size=1024,
                                                delay=1000)
        assert(packet_loss < 5)
        assert(buf_source)
        assert(buf_dest)


@pytest.mark.parametrize('nodes',
                         [pytest.param(['iotlab-m3', 'iotlab-m3'])],
                         indirect=['nodes'])
def test_task02(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0), RIOTNode_factory(1)]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = udp_send(
                                                nodes[i],
                                                nodes[i ^ 1],
                                                nodes[i ^ 1].get_ip_addr(),
                                                port=61616,
                                                count=1000,
                                                payload_size=1024,
                                                delay=1000)
        assert(packet_loss < 5)
        assert(buf_source)
        assert(buf_dest)


@pytest.mark.local_only
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native'])],
                         indirect=['nodes'])
def test_task03(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0, port='tap0')]
    _, buf_source, _ = udp_send(nodes[0],
                                None,
                                'fe80::bd:b7ec',
                                port=1337,
                                count=1000,
                                payload_size=8,
                                delay=0)
    assert(buf_source)


@pytest.mark.parametrize('nodes',
                         [pytest.param(['iotlab-m3'])],
                         indirect=['nodes'])
def test_task04(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0)]
    _, buf_source, _ = udp_send(nodes[0],
                                None,
                                'fe80::bd:b7ec',
                                port=1337,
                                count=1000,
                                payload_size=8,
                                delay=0)
    assert(buf_source)


@pytest.mark.local_only
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native', 'native'])],
                         indirect=['nodes'])
def test_task05(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0, port='tap0'),
             RIOTNode_factory(1, port='tap1')]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = udp_send(
                                                nodes[i],
                                                nodes[i ^ 1],
                                                nodes[i ^ 1].get_ip_addr(),
                                                port=1337,
                                                count=10,
                                                payload_size=0,
                                                delay=100)
        assert(packet_loss < 10)
        assert(buf_source)
        assert(buf_dest)


@pytest.mark.parametrize('nodes',
                         [pytest.param(['iotlab-m3', 'iotlab-m3'])],
                         indirect=['nodes'])
def test_task06(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0), RIOTNode_factory(1)]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = udp_send(
                                                nodes[i],
                                                nodes[i ^ 1],
                                                nodes[i ^ 1].get_ip_addr(),
                                                port=1337,
                                                count=10,
                                                payload_size=0,
                                                delay=100)
        assert(packet_loss < 10)
        assert(buf_source)
        assert(buf_dest)
