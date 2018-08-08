import string
import re
from time import sleep
import random
import os
import inspect
from traceback import print_tb
import sys
import pexpect
import signal
import io


def child_generator(*args, **kwargs):
    class ChildClass(Child, *args):
        pass
    return ChildClass


class Child:
    def __init__(self, cmd):
        self._cmd = cmd
        self.instance = None
        self.logger = None

    def write(self, cmd):
        self.instance.sendline("{}".format(cmd))

    def reboot(self):
        self.write("reboot")

    def expect(self, val, timeout=-1):
        return self.instance.expect(val, timeout=timeout)

    def connect(self):
        self.logger = io.StringIO()
        self.instance = pexpect.spawnu(self._cmd, codec_errors='replace', timeout=30, logfile=self.logger)
        self.instance.setecho(False)
        self.reboot()

    def disconnect(self):
        try:
            os.killpg(os.getpgid(self.instance.pid), signal.SIGKILL)
        except ProcessLookupError:
            print("Process already stopped")
        self.instance = None
        self.logger.close()
        self.logger = None

class TestRunner:
    def bootstrap(self, nodes, child, params):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def from_cmd(self, cmd_list):
        self._instances = [child_generator(*self.mixins)(cmd) for cmd in cmd_list]

    def connect(self):
        for child in self._instances:
            child.connect()

        sleep(1)

    def disconnect(self):
        for child in self._instances:
            child.disconnect()

    def run(self):
        riot_folder = os.environ.get("RIOTBASE", None)
        if not riot_folder:
            print("ERROR: Please provide RIOTBASE")
            sys.exit(1)

        os.chdir(os.path.join(riot_folder, self.test_location))
        self.bootstrap()

        tests = [t[1] for t in inspect.getmembers(self) if hasattr(t[1], "__dict__") and t[1].__dict__.get("__test__")]
        fail = False
        for t in tests:
            self.connect()
            nodes = self._instances
            print("Running test {} from {}".format(t.__name__, self.__class__))

            try:
                t(nodes)
                print("PASSED")
            except pexpect.TIMEOUT as e:
                print("FAILED")
                print(e.get_trace())
                fail = True
                print_tb(sys.exc_info()[2])
                break
            except:
                fail = True
                print_tb(sys.exc_info()[2])
                print("FAILED")

            self.disconnect()


        if not fail:
            print("All test passed!")
        self.stop()

