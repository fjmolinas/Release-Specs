import pytest

import sys
import os

from common import ping, print_results
from mixins import RIOTNodeShellIfconfig, RIOTNodeShellPktbuf
from iotlab import IOTLABNode, IoTLABExperiment


DEVNULL = open(os.devnull, 'w')


class SixLoWPANShell(RIOTNodeShellIfconfig, RIOTNodeShellPktbuf):
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
        exp = IoTLABExperiment(name="RIOT-release-test-04-01", nodes=nodes)
        exp.start()
        yield nodes
        exp.stop()

@pytest.fixture
def RIOTNode_factory(nodes):
    def gnrc_node(i, board_type=None, application_dir="examples/gnrc_networking",
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
        node.start_term()
        return SixLoWPANShell(node)
    return gnrc_node


@pytest.mark.parametrize('nodes',
                         [pytest.param(['iotlab-m3', 'iotlab-m3'])],
                         indirect=['nodes'])
def test_task01(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0), RIOTNode_factory(1)]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                 nodes[i ^ 1],
                                                 nodes[i ^ 1].get_ip_addr(),
                                                 1000,
                                                 0,
                                                 20,
                                                 26)
        assert(packet_loss < 10)
        assert(buf_source)
        assert(buf_dest)

@pytest.mark.parametrize('nodes',
                         [pytest.param(['samr21-xpro', 'iotlab-m3'])],
                         indirect=['nodes'])
def test_task02(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0), RIOTNode_factory(1)]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                 nodes[i ^ 1],
                                                 'ff02::1',
                                                 1000,
                                                 50,
                                                 100,
                                                 17)
        assert(packet_loss < 10)
        assert(buf_source)
        assert(buf_dest)

@pytest.mark.parametrize('nodes',
                         [pytest.param(['iotlab-m3', 'iotlab-m3'])],
                         indirect=['nodes'])
def test_task03(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0), RIOTNode_factory(1)]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                 nodes[i ^ 1],
                                                 nodes[i ^ 1].get_ip_addr(),
                                                 500,
                                                 1000,
                                                 300,
                                                 26)
        assert(packet_loss < 10)
        assert(buf_source)
        assert(buf_dest)

@pytest.mark.parametrize('nodes',
                         [pytest.param(['samr21-xpro', 'iotlab-m3'])],
                         indirect=['nodes'])
def test_task04(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0), RIOTNode_factory(1)]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                 nodes[i ^ 1],
                                                 nodes[i ^ 1].get_ip_addr(),
                                                 10000,
                                                 100,
                                                 100,
                                                 26)
        assert(packet_loss < 10)
        assert(buf_source)
        assert(buf_dest)

@pytest.mark.local_only
@pytest.mark.xfail
@pytest.mark.parametrize('nodes',
                         [pytest.param(['samr21-xpro', 'remote-revb'])],
                         indirect=['nodes'])
def test_task05(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0), RIOTNode_factory(1)]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                 nodes[i ^ 1],
                                                 nodes[i ^ 1].get_ip_addr(),
                                                 1000,
                                                 50,
                                                 100,
                                                 26)
        assert(packet_loss < 10)
        assert(buf_source)
        assert(buf_dest)

@pytest.mark.local_only
@pytest.mark.xfail
@pytest.mark.parametrize('nodes',
                         [pytest.param(['samr21-xpro', 'remote-revb'])],
                         indirect=['nodes'])
def test_task06(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0), RIOTNode_factory(1)]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                 nodes[i ^ 1],
                                                 'ff02::1',
                                                 1000,
                                                 50,
                                                 100,
                                                 17)
        assert(packet_loss < 10)
        assert(buf_source)
        assert(buf_dest)

@pytest.mark.xfail
@pytest.mark.parametrize('nodes',
                         [pytest.param(['samr21-xpro', 'arduino-zero'])],
                         indirect=['nodes'])
def test_task07(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0, board_type='arduino-zero',
                              modules='gnrc_pktbuf_cmd xbee'),
             RIOTNode_factory(0, board_type='samr21-xpro',
                              modules='gnrc_pktbuf_cmd')]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                 nodes[i ^ 1],
                                                 'ff02::1',
                                                 1000,
                                                 50,
                                                 150,
                                                 17)
        assert(packet_loss < 10)
        assert(buf_source)
        assert(buf_dest)

@pytest.mark.xfail
@pytest.mark.parametrize('nodes',
                         [pytest.param(['samr21-xpro', 'arduino-zero'])],
                         indirect=['nodes'])
def test_task08(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0, board_type='arduino-zero',
                              modules='gnrc_pktbuf_cmd xbee'),
             RIOTNode_factory(0, board_type='samr21-xpro',
                              modules='gnrc_pktbuf_cmd')]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                 nodes[i ^ 1],
                                                 nodes[i ^ 1].get_ip_addr(),
                                                 1000,
                                                 100,
                                                 100,
                                                 26)
        assert(packet_loss < 10)
        assert(buf_source)
        assert(buf_dest)

# ping timeouts, need to figure that test out...
@pytest.mark.xfail
@pytest.mark.parametrize('nodes',
                         [pytest.param(['iotlab-m3', 'iotlab-m3'])],
                         indirect=['nodes'])
def test_task09(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0), RIOTNode_factory(1)]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                 nodes[i ^ 1],
                                                 nodes[i ^ 1].get_ip_addr(),
                                                 200,
                                                 1232,
                                                 0,
                                                 26)
        assert(buf_source)
        assert(buf_dest)

@pytest.mark.parametrize('nodes',
                         [pytest.param(['iotlab-m3', 'iotlab-m3'])],
                         indirect=['nodes'])
def test_task10(nodes, RIOTNode_factory):
    nodes = [RIOTNode_factory(0, modules='gnrc_pktbuf_cmd gnrc_ipv6_ext_frag',
                              cflags='-DGNRC_PKTBUF_SIZE=8192'),
             RIOTNode_factory(1, modules='gnrc_pktbuf_cmd gnrc_ipv6_ext_frag',
                              cflags='-DGNRC_PKTBUF_SIZE=8192')]
    for i in range(0, 2):
        packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                 nodes[i ^ 1],
                                                 nodes[i ^ 1].get_ip_addr(),
                                                 200,
                                                 2048,
                                                 600,
                                                 26,
                                                 100)
        assert(packet_loss < 10)
        assert(buf_source)
        assert(buf_dest)