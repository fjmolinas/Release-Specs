"""
Helpers for pytest
"""

import os
import re
import subprocess

import pexpect.replwrap
import pytest

from .iotlab import IoTLABExperiment, DEFAULT_SITE, IOTLAB_DOMAIN


def list_from_string(list_str=None):
    """Get list of items from `list_str`

    >>> list_from_string(None)
    []
    >>> list_from_string("")
    []
    >>> list_from_string("  ")
    []
    >>> list_from_string("a")
    ['a']
    >>> list_from_string("a  ")
    ['a']
    >>> list_from_string("a b  c")
    ['a', 'b', 'c']
    """
    value = (list_str or '').split(' ')
    return [v for v in value if v]


def check_ssh():
    user, _ = IoTLABExperiment.user_credentials()
    if user is None:
        return False
    spawn = pexpect.spawnu("ssh {}@{}.{} /bin/bash".format(user, DEFAULT_SITE,
                                                           IOTLAB_DOMAIN))
    spawn.sendline("echo $USER")
    return bool(spawn.expect([pexpect.TIMEOUT, "{}".format(user)],
                             timeout=5))


def check_sudo():
    sudo_only_mark = None
    if os.geteuid() != 0:
        sudo_only_mark = pytest.mark.skip(reason="Test needs sudo to run")
    return sudo_only_mark


def check_local(run_local):
    local_only_mark = None
    if not run_local:
        local_only_mark = pytest.mark.skip(reason="Test can't run on IoT-LAB")
    return local_only_mark


def check_credentials(run_local):
    iotlab_creds_mark = None
    if not run_local and not IoTLABExperiment.check_user_credentials():
        iotlab_creds_mark = pytest.mark.skip(
            reason="Test requires IoT-LAB credentials in {}. "
                   "Use `iotlab-auth` to create".format(
                       os.path.join(os.environ["HOME"], ".iotlabrc"))
        )
    elif not run_local and not check_ssh():
        iotlab_creds_mark = pytest.mark.skip(
            reason="Can't access IoT-LAB front-end {}.{} via SSH. "
                   "Use key without password or `ssh-agent`".format(
                       DEFAULT_SITE, IOTLAB_DOMAIN)
        )
    return iotlab_creds_mark


def check_rc(only_rc_allowed):
    rc_only_mark = None
    output = subprocess.check_output([
        "git", "-C", os.environ["RIOTBASE"], "log", "-1", "--oneline",
        "--decorate"
    ]).decode()
    is_rc = re.search(r"tag:\s\d{4}.\d{2}-RC\d+", output) is not None

    if only_rc_allowed and not is_rc:
        rc_only_mark = pytest.mark.skip(
            reason="RIOT version under test is not a release candidate"
        )
    return rc_only_mark