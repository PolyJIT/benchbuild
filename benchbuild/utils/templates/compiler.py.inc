#!{python}
#
import os
import sys
import logging
import dill
from plumbum.commands.modifiers import TEE
from plumbum import ProcessExecutionError
from benchbuild.utils.cmd import timeout, sh
from benchbuild.utils.compiler import ExperimentCommand
from benchbuild.utils.run import exit_code_from_run_infos
from benchbuild.utils import log

os.environ["BB_CONFIG_FILE"] = "{CFG_FILE}"
from benchbuild.settings import CFG, update_env

log.configure()
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler(stream=sys.stderr))
log.setLevel(logging.DEBUG)

update_env()

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


def has_debug_enabled(flags):
    """
    Check, if -gXXX has been enabled.

    Not all of our transformations handle debug symbols well. With this
    method we can detect the case and handle it properly (strip the flags).
    """
    filtered = [x for x in flags if '-' is x[0] and len(x) > 1 and 'g' is x[1]]
    return len(filtered) > 0


def strip_debug_flags(flags):
    """Strip '-g*' flags from the command line."""
    flags = [x for x in flags if ('-' is not x[0]) or
                                 ('-' is x[0] and
                                   ((len(x) > 1) and ('g' is not x[1])))]
    return flags


def invoke_external_measurement(cmd):
    f = None
    if os.path.exists(BLOB_F):
        with open(BLOB_F, "rb") as p:
            f = dill.load(p)

    ret = None
    if f is not None:
        if not sys.stdin.isatty():
            ret = f(cmd, has_stdin=True)
        else:
            ret = f(cmd)
    return ret


def run(cmd):
    fc = timeout["2m", cmd]
    fc = fc.with_env(**cmd.envvars)
    fc = sh['-c', str(fc)]
    retcode, stdout, stderr = (fc & TEE)
    return (retcode, stdout, stderr)


def construct_cc(cc, flags, CFLAGS, LDFLAGS, ifiles):
    fc = None
    if has_debug_enabled(flags):
        flags = strip_debug_flags(flags)
    if len(input_files) > 0:
        fc = ExperimentCommand(cc, ["-Qunused-arguments"], [flags, CFLAGS, LDFLAGS])
    else:
        fc = ExperimentCommand(cc, ["-Qunused-arguments"], [flags])
    fc = fc.with_env(**cc.envvars)
    return fc


def construct_cc_default(cc, flags, ifiles):
    fc = None
    fc = ExperimentCommand(cc, ["-Qunused-arguments"], [flags])
    fc = fc.with_env(**cc.envvars)
    return fc


def main():
    if 'conftest.c' in input_files:
        retcode, _, _ = (CC[flags] & TEE)
        return retcode
    else:
        fc = construct_cc(CC, flags, CFLAGS, LDFLAGS, input_files)
        run_infos = None
        try:
            run_infos = invoke_external_measurement(fc)
            return exit_code_from_run_infos(run_infos)
        except ProcessExecutionError:
            fc = construct_cc_default(CC, flags, input_files)
            retcode, _, _ = run(fc)
            return retcode

if __name__ == "__main__":
    retcode = main()
    sys.exit(retcode)
