import pexpect
from decorators import task

class GNRCMixin:
    @task("Get IP address")
    def get_ip_addr(self):
        self.write("ifconfig")
        self.expect("inet6 addr: ([:0-9a-f]+) ")
        ip_addr = self.instance.match.group(1)
        return ip_addr

    @task("Get first interface")
    def get_first_iface(self):
        self.write("ifconfig")
        self.expect("Iface  ([\d]+)")
        return int(self.instance.match.group(1))

    @task("Disabling Router Advertisement")
    def disable_rdv(self, iface):
        self.write("ifconfig {} -rtr_adv".format(iface))
        self.expect("success")
    
    @task("Add IP address")
    def add_ip(self, iface, source):
        self.write("ifconfig {} add {}".format(iface, source))
        self.expect("success")

    @task("Add NIB route")
    def add_nib_route(self, iface, route, ip_addr):
        self.write("nib route add {} {} {}".format(iface, route, ip_addr))

    @task("Pinging node")
    def ping(self, count, dest_addr):
        self.write("ping6 {} {} 1024 10".format(count, dest_addr))
        packet_loss = None
        for i in range(count+1):
            exp = self.expect(["bytes from", "([\d]+) packets transmitted, ([\d]+) received, ([\d]+)% packet loss", "timeout",  pexpect.TIMEOUT], timeout=10)

            if exp == 1:
                packet_loss = int(self.instance.match.group(3))
                break
            if exp == 2:
                print("x", end="", flush=True)
            else:
                print(".", end="", flush=True)

        return packet_loss

class PktBufMixin:
    def extract_unused(self):
        self.write("pktbuf")
        self.expect("unused: ([0-9xa-f]+) ")
        return self.instance.match.group(1)

