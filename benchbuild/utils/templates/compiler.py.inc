#!/usr/bin/env python3
#
import os
import sys
import logging
import dill
import functools
from plumbum import ProcessExecutionError, local
from plumbum.commands.modifiers import TEE
from benchbuild.utils.cmd import timeout
from benchbuild.utils.run import GuardedRunException
from benchbuild.utils import log

os.environ["BB_CONFIG_FILE"] = "{CFG_FILE}"
from benchbuild.settings import CFG

log.configure()
log = logging.getLogger("benchbuild")
log.addHandler(logging.StreamHandler(stream=sys.stderr))
log.setLevel(logging.DEBUG)

CC_F = "{CC_F}"
CC = None
with open(CC_F, "rb") as cc_f:
    CC = dill.load(cc_f)
if not CC:
    log.error("Could not load the compiler command")
    sys.exit(1)

CFLAGS = {CFLAGS}
LDFLAGS = {LDFLAGS}
BLOB_F = "{BLOB_F}"

CFG["db"]["host"] = "{db_host}"
CFG["db"]["port"] = "{db_port}"
CFG["db"]["name"] = "{db_name}"
CFG["db"]["user"] = "{db_user}"
CFG["db"]["pass"] = "{db_pass}"

input_files = [x for x in sys.argv[1:] if '-' is not x[0]]
flags = sys.argv[1:]


def invoke_external_measurement(cmd):
    f = None
    if os.path.exists(BLOB_F):
        with open(BLOB_F,
                  "rb") as p:
            f = dill.load(p)

    if f is not None:
        if not sys.stdin.isatty():
            f(cmd, has_stdin=True)
        else:
            f(cmd)


def run(cmd):
    fc = timeout["2m", cmd]
    fc = fc.with_env(**cmd.envvars)
    retcode, stdout, stderr = (fc & TEE)
    return (retcode, stdout, stderr)


def construct_cc(cc, flags, CFLAGS, LDFLAGS, ifiles):
    fc = None
    if len(input_files) > 0:
        fc = cc["-Qunused-arguments", CFLAGS, LDFLAGS, flags]
    else:
        fc = cc["-Qunused-arguments", flags]
    fc = fc.with_env(**cc.envvars)
    return fc


def construct_cc_default(cc, flags, ifiles):
    fc = None
    fc = cc["-Qunused-arguments", flags]
    fc = fc.with_env(**cc.envvars)
    return fc


def main():
    if 'conftest.c' in input_files:
        retcode, _, _ = (CC[flags] & TEE)
        return retcode
    else:
        fc = construct_cc(CC, flags, CFLAGS, LDFLAGS, input_files)
        try:
            retcode, stdout, stderr = run(fc)
            invoke_external_measurement(fc)
            return retcode
        except ProcessExecutionError:
            fc = construct_cc_default(CC, flags, input_files)
            retcode, stdout, stderr = run(fc)
            return retcode

if __name__ == "__main__":
    retcode = main()
    sys.exit(retcode)
