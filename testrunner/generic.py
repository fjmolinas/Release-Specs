from testrunner import Child, TestRunner
import pexpect
import subprocess
import os
import signal
import getpass

class GenericTestRunner(TestRunner):
    def bootstrap(self, *args, **kwargs):
        child = pexpect.spawnu('/home/jialamos/Development/RIOT/dist/tools/tapsetup/tapsetup -c')

        if child.expect([pexpect.TIMEOUT, "[pP]ass"], timeout=2) != 0:
                passw = getpass.getpass('Password: ')
                child.sendline(passw)

        cmd = "make BOARD=native PORT=tap{} term"
        make = subprocess.check_call(["make", "BOARD=native", "clean", "all"])
        self.from_cmd([cmd.format(i) for i in range(self.nodes)])

    def stop(self):
        pass
