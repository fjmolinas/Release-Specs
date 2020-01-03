import pytest

import sys
import os

from common import ping, print_results
from mixins import RIOTNodeShellIfconfig, RIOTNodeShellPktbuf
from iotlab import IOTLABNode, IoTLABExperiment


DEVNULL = open(os.devnull, 'w')


class SixLoWPANShell(RIOTNodeShellIfconfig, RIOTNodeShellPktbuf):
    pass


@pytest.fixture(params=[
    ["iotlab-m3", "iotlab-m3"],
    ["iotlab-m3", "samr21-xpro"],
    ["arduino-zero", "samr21-xpro"],
    ])
def iotlab_experiment(request):
    nodes = []
    for board in request.param:
        env = {
            'BOARD': '{}'.format(board),
            'USEMODULE' : 'gnrc_pktbuf_cmd',
        }
        nodes.append(IOTLABNode(env=env))
    exp = IoTLABExperiment(name="RIOT-release-test-04-01", nodes=nodes)
    exp.start()
    yield exp
    exp.stop()

@pytest.fixture
def source(iotlab_experiment):
    riotbase = os.environ.get('RIOTBASE', None)
    os.chdir(os.path.join(riotbase, "examples/gnrc_networking"))
    iotlab_experiment.nodes[0].make_run(['flash'], stdout=DEVNULL, stderr=DEVNULL)
    iotlab_experiment.nodes[0].start_term()
    yield SixLoWPANShell(iotlab_experiment.nodes[0])
    iotlab_experiment.nodes[0].stop_term()

@pytest.fixture
def dest(iotlab_experiment):
    riotbase = os.environ.get('RIOTBASE', None)
    os.chdir(os.path.join(riotbase, "examples/gnrc_networking"))
    iotlab_experiment.nodes[1].make_run(['flash'], stdout=DEVNULL, stderr=DEVNULL)
    iotlab_experiment.nodes[1].start_term()
    yield SixLoWPANShell(iotlab_experiment.nodes[1])
    iotlab_experiment.nodes[0].stop_term()


@pytest.mark.parametrize('iotlab_experiment, dest_addr, count, size, delay, chan, tol',
                        [
                            pytest.param(
                                ['iotlab-m3', 'iotlab-m3'], None, 1000, 0,
                                10, 26, 10, id='task01'),
                            pytest.param(
                                ['iotlab-m3', 'samr21-xpro'], 'ff02::1', 1000, 50,
                                100, 17, 10, id='task02'),
                            pytest.param(
                                ['iotlab-m3', 'iotlab-m3'], None, 1000, 1000,
                                100, 26, 10, id='task03'),
                            pytest.param(
                                ['iotlab-m3', 'samr21-xpro'], None, 10000, 100,
                                100, 26, 10, id='task04'),
                            pytest.param(
                                ['arduino-zero', 'samr21-xpro'], None, 1000, 150,
                                50, 17, 10, id='task07'),
                            pytest.param(
                                ['arduino-zero', 'samr21-xpro'], None, 1000, 350,
                                100, 26, 10, id='task08'),
                            pytest.param(
                                ['iotlab-m3', 'iotlab-m3'], None, 1000, 200,
                                1232, 26, 100, id='task09'),

                        ],indirect=['iotlab_experiment']
                    )
def test_single_hop_6lowpan_icmp(iotlab_experiment, source, dest, dest_addr, count, size, delay, chan, tol):
    if dest_addr is None:
        dest_addr = dest.get_ip_addr()
    packet_loss, buf_source, buf_dest = ping(source,
                                          dest,
                                          dest_addr,
                                          count,
                                          size,
                                          delay,
                                          chan)
    assert(packet_loss < tol)
    assert(buf_source)
    assert(buf_dest)