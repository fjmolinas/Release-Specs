import pexpect

class RIOTNodeShellIfconfig():

    def __init__(self, node):
        self.term = node.term

    def reboot(self):
        self.term.sendline("reboot")
        self.term.expect_exact("RIOT")

    def get_ip_addr(self):
        self.term.sendline("ifconfig")
        self.term.expect(r"inet6 addr: (?P<lladdr>[0-9a-fA-F:]+:[A-Fa-f:0-9]+)"
                          "  scope: link  VAL")
        ip_addr = self.term.match.group(1)
        return ip_addr

    def get_first_iface(self):
        self.term.sendline("ifconfig")
        self.term.expect(r"Iface  ([\d]+)")
        return int(self.term.match.group(1))

    def disable_rdv(self, iface):
        self.term.sendline("ifconfig {} -rtr_adv".format(iface))
        self.term.expect_exact("success")

    def add_ip(self, iface, source):
        self.term.sendline("ifconfig {} add {}".format(iface, source))
        self.term.expect_exact("success")

    def set_chan(self, iface, chan):
        self.term.sendline("ifconfig {} set chan {}".format(iface, chan))
        self.term.expect_exact("success: set channel on interface {} to {}"
                               .format(iface, chan))

    def add_nib_route(self, iface, route, ip_addr):
        self.term.sendline(
                "nib route add {} {} {}".format(iface, route, ip_addr))

    def ping(self, count, dest_addr, payload_size, delay):
        self.term.sendline("ping6 {} -s {} -i {} -c {} "
                           .format(dest_addr, payload_size, delay, count))
        packet_loss = None
        for i in range(count+1):
            exp = self.term.expect(
                    ["bytes from",r"(\d+) packets transmitted, (\d+) packets received, (\d+)% packet loss",
                     "timeout", pexpect.TIMEOUT],
                    timeout=10)
            if exp == 1:
                packet_loss = int(self.term.match.group(3))
                break
            if exp == 2:
                print("x", end="", flush=True)
            else:
                print(".", end="", flush=True)

        return packet_loss


class GNRC_UDP():

    def __init__(self, node):
        self.term = node

    def udp_server_start(self, port):
        self.term.sendline("udp server start {}".format(port))
        self.term.expect_exact(
                "Success: started UDP server on port {}".format(port)
            )

    def udp_server_stop(self):
        self.term.sendline("udp server stop")

    def udp_server_check_output(self, count, delay_ms):
        packets_lost = 0
        for i in range(count):
            exp = self.term.expect([
                   r"Packets received: \d+",
                   r"PKTDUMP: data received:\n"
                   r"~~ SNIP  0 - size:  \d+ byte, type: NETTYPE_UNDEF \(\d+\)\n"
                   r".*\n"
                   r"~~ SNIP  1 - size:   8 byte, type: NETTYPE_UDP \(\d+\)\n"
                   r"   src-port:  \d+  dst-port:  \d+\n"
                   r"   length: \d+  cksum: 0x[0-9A-Fa-f]+\n"
                   r"~~ SNIP  2 - size:  40 byte, type: NETTYPE_IPV6 \(\d+\)\n"
                   r".*\n"
                   r"~~ SNIP  3 - size:  20 byte, type: NETTYPE_NETIF \(-1\)\n"
                   r"if_pid: \d.*"
                   r"~~ PKT    -  4 snips, total size:  \d+ byte",
                   pexpect.TIMEOUT
                ], timeout=(delay_ms / 1000) * 2)
            if exp in [0, 1]:
                print(".", end="", flush=True)
            else:
                packets_lost += 0
                print("x", end="", flush=True)
        return int((packets_lost / count) * 100)

    def udp_send(self, dest_addr, port, payload, count=1, delay_ms=1000):
        self.term.sendline(
                "udp send {} {} {} {} {}".format(
                    dest_addr, port, payload, count, delay_ms * 1000))
        try:
            payload = int(payload)
            bytes = payload
        except ValueError:
            bytes = len(payload)
        for _ in range(count):
            self.term.expect([
                "Success: sent {} byte\(s\) to \[{}\]:{}".format(
                    bytes, dest_addr, port),
                "Success: send {} byte to \[{}\]:{}".format(
                    bytes, dest_addr, port)
            ])


class RIOTNodeShellPktbuf():

    def __init__(self, node):
        self.term = node

    def is_empty(self):
        self.term.sendline("pktbuf")
        self.term.expect(r"packet buffer: "
                         r"first byte: 0x(?P<first_byte>[0-9A-Fa-f]+), "
                         r"last byte: 0x[0-9A-Fa-f]+ "
                         r"\(size: (?P<size>\d+)\)")
        exp_first_byte = int(self.term.match.group("first_byte"), base=16)
        exp_size = int(self.term.match.group("size"))
        exp = self.term.expect([r"~ unused: 0x(?P<first_byte>[0-9A-Fa-f]+) "
                                r"\(next: ((\(nil\))|0), "
                                r"size: (?P<size>\d+)\) ~",
                                pexpect.TIMEOUT])
        if exp == 0:
            first_byte = int(self.term.match.group("first_byte"), base=16)
            size = int(self.term.match.group("size"))
            return (exp_first_byte == first_byte) and (exp_size == size)
        else:
            return False
