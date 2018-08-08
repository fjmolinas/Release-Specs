from testrunner import TestRunner
import pexpect
import json
import subprocess
import re
from time import sleep

IOTLAB_SITE="grenoble"

class IotlabTestRunner(TestRunner):
    def generate(self, params=""):
        print("Booking nodes...")
        output = pexpect.run('make BOARD=iotlab-m3 IOTLAB_NODES={} IOTLAB_SITE={} {} iotlab-exp'.format(self.nodes, IOTLAB_SITE, params), timeout=600, encoding="utf-8")
        m = re.search('Waiting that experiment ([0-9]+) gets in state Running', output)

        if m and m.group(1):
            expId = m.group(1)
        else:
            print("Experiment id could not be parsed")
            return None
        return expId

    def get_nodes_addresses(self):
        output = subprocess.check_output(['experiment-cli', 'get', '-i', str(self.exp_id), '-r'], encoding="utf-8")
        res = json.loads(output)
        l = []
        for i in res["items"]:
            l.append(i["network_address"])

        print(l)
        return l

    def bootstrap(self):
        self.exp_id = self.generate()
        cmd = "make IOTLAB_NODE={} BOARD=iotlab-m3 term"
        self.from_cmd([cmd.format(n) for n in self.get_nodes_addresses()])
        sleep(2)

    def stop(self):
        subprocess.check_call(['experiment-cli', 'stop', '-i', str(self.exp_id)])

