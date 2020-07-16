import pytest

import time
import os

from common import ping
from testutils.mixins import RIOTNodeShellIfconfig, RIOTNodeShellPktbuf, RIOTNodeShellIfconfigOFDM
from testutils.iotlab import IOTLABNode, IoTLABExperiment


DEVNULL = open(os.devnull, 'w')


class SixLoWPANShell(RIOTNodeShellIfconfig, RIOTNodeShellPktbuf, RIOTNodeShellIfconfigOFDM):
    pass


@pytest.fixture
def nodes(local, request, boards):
    nodes = []
    boards_input = boards if boards else request.param
    if local is True:
        for board in boards_input:
            env = {'BOARD': '{}'.format(board)}
            nodes.append(IOTLABNode(env=env))
        yield nodes
    else:
        for board in boards_input:
            if IoTLABExperiment.valid_board(board):
                env = {'BOARD': '{}'.format(board)}
            else:
                env = {'IOTLAB_NODE': '{}'.format(board)}
            nodes.append(IOTLABNode(env=env))
        exp = IoTLABExperiment(name="RIOT-release-test-04", nodes=nodes)
        exp.start()
        yield nodes
        exp.stop()


@pytest.fixture
def RIOTNode_factory(nodes, riotbase):

    factory_nodes = []

    def gnrc_node(i, board_type=None,
                  application_dir="examples/gnrc_networking",
                  modules='gnrc_pktbuf_cmd', cflags='', idx=None,
                  dis_modules=''):
        if board_type is not None:
            node = next(n for n in nodes if n.board() == board_type)
        else:
            node = nodes[i]
        node.env['USEMODULE'] = modules
        node.env['CFLAGS'] = cflags
        node.env['DISABLE_MODULE'] = dis_modules
        if idx is not None:
            node.env['BOARD_INDEX'] = str(idx)
        node._application_directory = os.path.join(riotbase, application_dir)
        node.make_run(['flash'], stdout=DEVNULL, stderr=DEVNULL)
        # Some boards need a delay to start
        time.sleep(3)
        node.start_term()
        factory_nodes.append(node)
        return SixLoWPANShell(node)

    yield gnrc_node

    for node in factory_nodes:
        try:
            node.stop_term()
        except RuntimeError:
            # Process had to be forced kill, happens with native
            pass


@pytest.mark.parametrize('nodes',
                         [pytest.param(['openmote-b', 'openmote-b'])],
                         indirect=['nodes'])
def test_task01(nodes, RIOTNode_factory):
    nodes = [
        RIOTNode_factory(0, idx=0, dis_modules='at86rf215_subghz'),
        RIOTNode_factory(1, idx=1, dis_modules='at86rf215_subghz')]

    for mcs in range(0, 6):
        for i in range(0, 2):
            itf = nodes[i].get_first_iface()
            nodes[i].set_mode(itf, 'mr-ofdm')
            nodes[i].set_mcs(itf, mcs)
            nodes[i].set_opt(itf, 1)
        for i in range(0, 2):
            packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                    nodes[i ^ 1],
                                                    nodes[i ^ 1].get_ip_addr(),
                                                    count=100,
                                                    payload_size=100,
                                                    delay=100)
            assert(packet_loss < 10)
            assert(buf_source)
            assert(buf_dest)


@pytest.mark.parametrize('nodes',
                         [pytest.param(['openmote-b', 'openmote-b'])],
                         indirect=['nodes'])
def test_task02(nodes, RIOTNode_factory):
    nodes = [
        RIOTNode_factory(0, idx=0, dis_modules='at86rf215_subghz'),
        RIOTNode_factory(1, idx=1, dis_modules='at86rf215_subghz')]

    for mcs in range(0, 6):
        for i in range(0, 2):
            itf = nodes[i].get_first_iface()
            nodes[i].set_mode(itf, 'mr-ofdm')
            nodes[i].set_mcs(itf, mcs)
            nodes[i].set_opt(itf, 2)
        for i in range(0, 2):
            packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                    nodes[i ^ 1],
                                                    nodes[i ^ 1].get_ip_addr(),
                                                    count=100,
                                                    payload_size=100,
                                                    delay=100)
            assert(packet_loss < 10)
            assert(buf_source)
            assert(buf_dest)


@pytest.mark.parametrize('nodes',
                         [pytest.param(['openmote-b', 'openmote-b'])],
                         indirect=['nodes'])
def test_task03(nodes, RIOTNode_factory):
    nodes = [
        RIOTNode_factory(0, idx=0, dis_modules='at86rf215_subghz'),
        RIOTNode_factory(1, idx=1, dis_modules='at86rf215_subghz')]

    for mcs in range(1, 6):
        for i in range(0, 2):
            itf = nodes[i].get_first_iface()
            nodes[i].set_mode(itf, 'mr-ofdm')
            nodes[i].set_mcs(itf, mcs)
            nodes[i].set_opt(itf, 3)
        for i in range(0, 2):
            packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                    nodes[i ^ 1],
                                                    nodes[i ^ 1].get_ip_addr(),
                                                    count=100,
                                                    payload_size=100,
                                                    delay=100)
            assert(packet_loss < 10)
            assert(buf_source)
            assert(buf_dest)


@pytest.mark.parametrize('nodes',
                         [pytest.param(['openmote-b', 'openmote-b'])],
                         indirect=['nodes'])
def test_task04(nodes, RIOTNode_factory):
    nodes = [
        RIOTNode_factory(0, idx=0, dis_modules='at86rf215_subghz'),
        RIOTNode_factory(1, idx=1, dis_modules='at86rf215_subghz')]

    for mcs in range(2, 6):
        for i in range(0, 2):
            itf = nodes[i].get_first_iface()
            nodes[i].set_mode(itf, 'mr-ofdm')
            nodes[i].set_mcs(itf, mcs)
            nodes[i].set_opt(itf, 4)
        print("running at mcs {}".format(mcs))
        for i in range(0, 2):
            packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                    nodes[i ^ 1],
                                                    nodes[i ^ 1].get_ip_addr(),
                                                    count=100,
                                                    payload_size=100,
                                                    delay=100)
            assert(packet_loss < 10)
            assert(buf_source)
            assert(buf_dest)


@pytest.mark.parametrize('nodes',
                         [pytest.param(['openmote-b', 'openmote-b'])],
                         indirect=['nodes'])
def test_task05(nodes, RIOTNode_factory):
    nodes = [
        RIOTNode_factory(0, idx=0, dis_modules='at86rf215_24ghz'),
        RIOTNode_factory(1, idx=1, dis_modules='at86rf215_24ghz')]


    for mcs in range(0, 6):
        for i in range(0, 2):
            itf = nodes[i].get_first_iface()
            nodes[i].set_mode(itf, 'mr-ofdm')
            nodes[i].set_mcs(itf, mcs)
            nodes[i].set_opt(itf, 1)
        for i in range(0, 2):
            packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                    nodes[i ^ 1],
                                                    nodes[i ^ 1].get_ip_addr(),
                                                    count=100,
                                                    payload_size=100,
                                                    delay=100)
            assert(packet_loss < 10)
            assert(buf_source)
            assert(buf_dest)


@pytest.mark.parametrize('nodes',
                         [pytest.param(['openmote-b', 'openmote-b'])],
                         indirect=['nodes'])
def test_task06(nodes, RIOTNode_factory):
    nodes = [
        RIOTNode_factory(0, idx=0, dis_modules='at86rf215_24ghz'),
        RIOTNode_factory(1, idx=1, dis_modules='at86rf215_24ghz')]

    for mcs in range(0, 6):
        for i in range(0, 2):
            itf = nodes[i].get_first_iface()
            nodes[i].set_mode(itf, 'mr-ofdm')
            nodes[i].set_mcs(itf, mcs)
            nodes[i].set_opt(itf, 2)
        for i in range(0, 2):
            packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                    nodes[i ^ 1],
                                                    nodes[i ^ 1].get_ip_addr(),
                                                    count=100,
                                                    payload_size=100,
                                                    delay=100)
            assert(packet_loss < 10)
            assert(buf_source)
            assert(buf_dest)


@pytest.mark.parametrize('nodes',
                         [pytest.param(['openmote-b', 'openmote-b'])],
                         indirect=['nodes'])
def test_task07(nodes, RIOTNode_factory):
    nodes = [
        RIOTNode_factory(0, idx=0, dis_modules='at86rf215_24ghz'),
        RIOTNode_factory(1, idx=1, dis_modules='at86rf215_24ghz')]

    for mcs in range(1, 6):
        for i in range(0, 2):
            itf = nodes[i].get_first_iface()
            nodes[i].set_mode(itf, 'mr-ofdm')
            nodes[i].set_mcs(itf, mcs)
            nodes[i].set_opt(itf, 3)
        for i in range(0, 2):
            packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                    nodes[i ^ 1],
                                                    nodes[i ^ 1].get_ip_addr(),
                                                    count=100,
                                                    payload_size=100,
                                                    delay=100)
            assert(packet_loss < 10)
            assert(buf_source)
            assert(buf_dest)


@pytest.mark.parametrize('nodes',
                         [pytest.param(['openmote-b', 'openmote-b'])],
                         indirect=['nodes'])
def test_task08(nodes, RIOTNode_factory):
    nodes = [
        RIOTNode_factory(0, idx=0, dis_modules='at86rf215_24ghz'),
        RIOTNode_factory(1, idx=1, dis_modules='at86rf215_24ghz')]

    for mcs in range(2, 6):
        for i in range(0, 2):
            itf = nodes[i].get_first_iface()
            nodes[i].set_mode(itf, 'mr-ofdm')
            nodes[i].set_mcs(itf, mcs)
            nodes[i].set_opt(itf, 4)
        for i in range(0, 2):
            packet_loss, buf_source, buf_dest = ping(nodes[i],
                                                    nodes[i ^ 1],
                                                    nodes[i ^ 1].get_ip_addr(),
                                                    count=100,
                                                    payload_size=100,
                                                    delay=100)
            assert(packet_loss < 10)
            assert(buf_source)
            assert(buf_dest)
