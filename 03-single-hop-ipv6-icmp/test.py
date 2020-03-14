import os
import pytest
import time

from common import ping
from testutils.mixins import RIOTNodeShellIfconfig, RIOTNodeShellPktbuf
from testutils.iotlab import IOTLABNode, IoTLABExperiment


DEVNULL = open(os.devnull, 'w')
IOTLAB_EXPERIMENT_DURATION = 120


class SixLoWPANShell(RIOTNodeShellIfconfig, RIOTNodeShellPktbuf):
    pass


@pytest.fixture
def nodes(local, request):
    nodes = []
    for board in request.param:
        env = {'BOARD': '{}'.format(board)}
        nodes.append(IOTLABNode(env=env))
    # Start iot-lab experiment if requested
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


@pytest.mark.local_only
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native', 'native'])],
                         indirect=['nodes'])
def test_task01(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0, port='tap0'),
             RIOTNode_factory(1, port='tap1')]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                 nodes[i ^ 1],
                                                 'ff02::1',
                                                 count=1000,
                                                 payload_size=0,
                                                 delay=10)
        assert(packet_loss < 1)
        assert(buf_source)
        assert(buf_dest)


@pytest.mark.local_only
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native', 'native'])],
                         indirect=['nodes'])
def test_task02(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0, port='tap0'),
             RIOTNode_factory(1, port='tap1')]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                 nodes[i ^ 1],
                                                 nodes[i ^ 1].get_ip_addr(),
                                                 count=1000,
                                                 payload_size=1000,
                                                 delay=100)
        assert(packet_loss < 1)
        assert(buf_source)
        assert(buf_dest)


@pytest.mark.local_only
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native', 'native'])],
                         indirect=['nodes'])
def test_task03(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0, port='tap0'),
             RIOTNode_factory(1, port='tap1')]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                 nodes[i ^ 1],
                                                 nodes[i ^ 1].get_ip_addr(),
                                                 count=3600,
                                                 payload_size=1000,
                                                 delay=1000)
        assert(packet_loss < 1)
        assert(buf_source)
        assert(buf_dest)


@pytest.mark.local_only
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native', 'native'])],
                         indirect=['nodes'])
def test_task06(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0,
                              modules='gnrc_pktbuf_cmd gnrc_ipv6_ext_frag',
                              cflags='-DGNRC_PKTBUF_SIZE=8192',
                              port='tap0'),
             RIOTNode_factory(1,
                              modules='gnrc_pktbuf_cmd gnrc_ipv6_ext_frag',
                              cflags='-DGNRC_PKTBUF_SIZE=8192',
                              port='tap1')]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                 nodes[i ^ 1],
                                                 nodes[i ^ 1].get_ip_addr(),
                                                 count=1000,
                                                 payload_size=2000,
                                                 delay=100,
                                                 empty_wait=30)
        assert(packet_loss < 1)
        assert(buf_source)
        assert(buf_dest)
