import sys
sys.path.append("../testrunner")

from iotlab import IotlabTestRunner
from generic import GenericTestRunner
from time import sleep
from mixins import GNRCMixin, PktBufMixin
from decorators import test


def helper(c1, c2, disable_rdv, count=100, route="::", source=None, dest=None):
    iface = c1.get_first_iface()
    if (disable_rdv):
        c1.disable_rdv(iface)
        c2.disable_rdv(iface)
    ip_addr = c2.get_ip_addr()
    ip_addr_2 = c1.get_ip_addr()

    if(source):
        c1.add_ip(iface, source)

    if(dest):
        c2.add_ip(iface, dest)

    c1.add_nib_route(iface, route, ip_addr)
    c2.add_nib_route(iface, route, ip_addr_2)

    return c1.ping(count, dest.split("/")[0])

class TestIotLab(IotlabTestRunner):
    nodes = 2
    test_location = "tests/gnrc_udp"
    mixins = [GNRCMixin, PktBufMixin]

    @test
    def task2(self, nodes):
        c1 = nodes[0]
        c2 = nodes[1]

        packet_loss = helper(c1, c2, False, source="affe::1/120", dest="beef::1/64")

        assert(packet_loss < 10)

class TestNative(GenericTestRunner):
    nodes = 2
    test_location = "tests/gnrc_udp"
    mixins = [GNRCMixin, PktBufMixin]

    @test
    def task1(self, nodes):
        c1 = nodes[0]
        c2 = nodes[1]

        packet_loss = helper(c1, c2, True, source="beef::2/64", dest="beef::1/64")

        assert(packet_loss < 1)

    @test
    def task3(self, nodes):
        c1 = nodes[0]
        c2 = nodes[1]

        packet_loss = helper(c1, c2, True, count=10, route="beef::/64", source="beef::2/64", dest="beef::1/64")

        assert(packet_loss < 1)

    @test
    def task4(self, nodes):
        c1 = nodes[0]
        c2 = nodes[1]

        packet_loss = helper(c1, c2, True, count=10, dest="beef::1/64")

        assert(packet_loss < 1)

TestIotLab().run()
TestNative().run()
