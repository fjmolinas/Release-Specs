import pytest

import sys
import time
import os

from common import single_hop_run, print_results
from mixins import RIOTNodeShellIfconfig, RIOTNodeShellPktbuf
from iotlab import IOTLABNode, IoTLABExperiment


DEVNULL = open(os.devnull, 'w')
IOTLAB_EXPERIMENT_DURATION = 120


class SingleHopNode(RIOTNodeShellIfconfig, RIOTNodeShellPktbuf):
    pass

@pytest.fixture
def nodes(local, request):
    nodes = []
    for board in request.param:
        env = { 'BOARD': '{}'.format(board) }
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
def RIOTNode_factory(nodes):
    def gnrc_node(i, board_type=None, application_dir="examples/gnrc_networking",
                  modules='gnrc_pktbuf_cmd', cflags=None, port=None):
        riotbase = os.environ.get('RIOTBASE', None)
        os.chdir(os.path.join(riotbase, application_dir))
        if board_type is not None:
            node = next(n for n in nodes if n.board() == board_type)
        else:
            node = nodes[i]
        node.env['USEMODULE'] = modules
        if cflags is not None:
            node.env['CFLAGS'] = cflags
        if port is not None:
            node.env['PORT'] = port
        node.make_run(['flash'], stdout=DEVNULL, stderr=DEVNULL)
        # Some boards need a delay to start
        time.sleep(3)
        node.start_term()
        return SingleHopNode(node)
    
    yield gnrc_node
    
    for node in nodes:
        node.stop_term()


@pytest.mark.local_only
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native', 'native'])],
                         indirect=['nodes'])
def test_task01(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0, port='tap0'), RIOTNode_factory(1, port='tap1')]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = single_hop_run(nodes[i],
                                                           nodes[i ^ 1],
                                                           'affe::2/64',
                                                           'beef::1/64',
                                                           '::',
                                                           '::',
                                                           rdv=False,
                                                           count=100,
                                                           payload_size=1000)
        assert(packet_loss < 1)
        assert(buf_source)
        assert(buf_dest)

@pytest.mark.parametrize('nodes',
                         [pytest.param(['iotlab-m3', 'iotlab-m3'])],
                         indirect=['nodes'])
def test_task02(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0), RIOTNode_factory(1)]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = single_hop_run(nodes[i],
                                                           nodes[i ^ 1],
                                                           'affe::1/120',
                                                           'beef::1/64',
                                                           '::',
                                                           '::',
                                                           rdv=False,
                                                           count=100,
                                                           payload_size=1000)
        assert(packet_loss < 1)
        assert(buf_source)
        assert(buf_dest)

@pytest.mark.local_only
@pytest.mark.parametrize('nodes',
                         [pytest.param(['native', 'native'])],
                         indirect=['nodes'])
def test_task03(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0, port='tap0'), RIOTNode_factory(1, port='tap1')]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = single_hop_run(nodes[i],
                                                           nodes[i ^ 1],
                                                           'beef::2/64',
                                                           'beef::1/64',
                                                           'beef::/64',
                                                           'beef::/64',
                                                           rdv=False,
                                                           count=10,
                                                           payload_size=1000)
        assert(packet_loss < 1)
        assert(buf_source)
        assert(buf_dest)

@pytest.mark.parametrize('nodes',
                         [pytest.param(['iotlab-m3', 'iotlab-m3'])],
                         indirect=['nodes'])
def test_task04(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0), RIOTNode_factory(1)]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = single_hop_run(nodes[i],
                                                           nodes[i ^ 1],
                                                           None,
                                                           'beef::1/6',
                                                           '::',
                                                           '::',
                                                           rdv=False,
                                                           count=100,
                                                           payload_size=1000)
        assert(packet_loss < 1)
        assert(buf_source)
        assert(buf_dest)
