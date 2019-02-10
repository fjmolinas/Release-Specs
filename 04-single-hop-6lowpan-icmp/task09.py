#! /usr/bin/env python3
# Copyright (C) 2018 Freie Universität Berlin
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

import sys
import os
import time

COUNT           = 200
PAYLOAD_SIZE    = 1232
DELAY           = 0     # ms
CHANNEL         = 26


def task09(riotbase, runs=1):
    os.chdir(os.path.join(riotbase, "examples/gnrc_networking"))
    try:
        exp = IoTLABExperiment("RIOT-release-test-04-09",
                               [IoTLABNode(extra_modules=["gnrc_pktbuf_cmd"]),
                                IoTLABNode(extra_modules=["gnrc_pktbuf_cmd"])])
    except Exception as e:
        print(str(e))
        print("Can't start experiment")
        return

    try:
        addrs = exp.nodes_addresses
        iotlab_cmd = "make IOTLAB_NODE={} BOARD=iotlab-m3 term"
        source = SixLoWPANNode(iotlab_cmd.format(addrs[0]))
        dest = SixLoWPANNode(iotlab_cmd.format(addrs[1]))
        results = []

        for run in range(runs):
            print("Run {}/{}: ".format(run + 1, runs), end="")
            packet_loss, buf_source, buf_dest = ping(source, dest,
                                                     dest.get_ip_addr(), COUNT,
                                                     PAYLOAD_SIZE, DELAY,
                                                     CHANNEL)
            results.append([packet_loss, buf_source, buf_dest])

            time.sleep(3)
            assert(source.is_empty())
            assert(dest.is_empty())
            assert(buf_source)
            assert(buf_dest)
            _, buf_source, buf_dest = ping(source, dest, dest.get_ip_addr(),
                                           2, 10, 10)
            assert(buf_source)
            assert(buf_dest)
            print("OK")
        print_results(results)
    except Exception as e:
        print("FAILED")
        print(str(e))
    finally:
        exp.stop()


if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 "../", "testutils"))
    from iotlab import IoTLABNode, IoTLABExperiment
    from common import argparser, SixLoWPANNode, ping, print_results

    args = argparser.parse_args()
    task09(**vars(args))
