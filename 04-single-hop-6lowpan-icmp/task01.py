#! /usr/bin/env python3
# Copyright (C) 2018 Freie Universität Berlin
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

import sys
import os

from common import argparser, ping, print_results
from mixins import RIOTNodeShellIfconfig, RIOTNodeShellPktbuf
from iotlab import IOTLABNode, IoTLABExperiment


COUNT           = 1000
PAYLOAD_SIZE    = 0
DELAY           = 100   # ms
CHANNEL         = 26
ERROR_TOLERANCE = 10    # %

DEVNULL = open(os.devnull, 'w')

class SixLoWPANShell(RIOTNodeShellIfconfig, RIOTNodeShellPktbuf):
    pass


def task01(riotbase, runs=1):
    os.chdir(os.path.join(riotbase, "examples/gnrc_networking"))

    env = {
        'BOARD': 'iotlab-m3',
        'USEMODULE' : 'gnrc_pktbuf_cmd',
    }
    nodes = [IOTLABNode(env=env), IOTLABNode(env=env)]

    exp = IoTLABExperiment(name="RIOT-release-test-04-01", nodes=nodes)
    exp.start()

    try:
        for node in nodes:
            node.make_run(['flash'], stdout=DEVNULL, stderr=DEVNULL)
            node.start_term()
        source = SixLoWPANShell(nodes[0])
        dest = SixLoWPANShell(nodes[1])
        results = []

        for run in range(runs):
            print("Run {}/{}: ".format(run + 1, runs), end="")
            packet_loss, buf_source, buf_dest = ping(source, dest,
                                                     dest.get_ip_addr(), COUNT,
                                                     PAYLOAD_SIZE, DELAY,
                                                     CHANNEL)
            results.append([packet_loss, buf_source, buf_dest])

            assert(packet_loss < ERROR_TOLERANCE)
            assert(buf_source)
            assert(buf_dest)
            print("OK")
        print_results(results)
    except Exception as e:
        print("FAILED")
        print(str(e))
    finally:
        nodes[0].stop_term()
        nodes[1].stop_term()
        exp.stop()

if __name__ == "__main__":
    args = argparser.parse_args()
    task01(**vars(args))
