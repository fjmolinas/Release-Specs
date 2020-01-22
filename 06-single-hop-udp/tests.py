import pytest

import sys
import time
import os

from common import udp_send, print_results
from mixins import RIOTNodeShellIfconfig, RIOTNodeShellPktbuf, RIOTNodeShellUdp
from iotlab import IOTLABNode, IoTLABExperiment


DEVNULL = open(os.devnull, 'w')


class SixLoWPANShell(RIOTNodeShellIfconfig,
                     RIOTNodeShellPktbuf,
                     RIOTNodeShellUdp):
    pass


@pytest.fixture
def nodes(local, request):
    nodes = []
    for board in request.param:
        env = { 'BOARD': '{}'.format(board) }
        nodes.append(IOTLABNode(env=env))
    if local is True:
        yield nodes
    else:
        exp = IoTLABExperiment(name="RIOT-release-test-06", nodes=nodes)
        exp.start(duration=120)
        yield nodes
        exp.stop()

@pytest.fixture
def RIOTNode_factory(nodes):
    def gnrc_node(i, board_type=None, application_dir="tests/gnrc_udp",
                  modules='gnrc_pktbuf_cmd', cflags=''):
        riotbase = os.environ.get('RIOTBASE', None)
        os.chdir(os.path.join(riotbase, application_dir))
        if board_type is not None:
            node = next(n for n in nodes if n.board() == board_type)
        else:
            node = nodes[i]
        node.env['USEMODULE'] = modules
        node.env['CFLAGS'] = cflags
        node.make_run(['flash'], stdout=DEVNULL, stderr=DEVNULL)
        # Some boards need a delay to start
        time.sleep(3)
        node.start_term()
        return SixLoWPANShell(node)
    return gnrc_node


@pytest.mark.parametrize('nodes',
                         [pytest.param(['iotlab-m3', 'iotlab-m3'])],
                         indirect=['nodes'])
def test_task01(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0), RIOTNode_factory(1)]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = udp_send(nodes[i],
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
        packet_loss, buf_source, buf_dest = udp_send(nodes[i],
                                                 nodes[i ^ 1],
                                                 nodes[i ^ 1].get_ip_addr(),
                                                 port=61616,
                                                 count=1000,
                                                 payload_size=1024,
                                                 delay=1000)
        assert(packet_loss < 5)
        assert(buf_source)
        assert(buf_dest)
