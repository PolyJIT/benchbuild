#!{{ python|default("/usr/bin/env python3") }}
#
import os
import sys

from plumbum import TEE

from benchbuild.utils import log
from benchbuild.utils.db import persist_project
from benchbuild.utils.run import exit_code_from_run_infos
from benchbuild.utils.wrapping import load

PROJECT = load("{{ project_file }}")
#EXPERIMENT = load("{{ experiment_file }}")
COMPILER = load("{{ cc_f }}")


def update_project(argv):
    if {{detect_project}}:
        name = PROJECT.name
        for arg in argv:
            if os.path.exists(arg):
                name = os.path.basename(os.path.normpath(os.path.dirname(arg)))
                break
        PROJECT.name = name
        persist_project(PROJECT)


def main(argv):
    log.configure()
    log.set_defaults()

    command_args = argv[1:]
    if COMPILER is None:
        sys.exit(1)

    if PROJECT is None:
        sys.exit(2)

    if PROJECT.compiler_extension is None:
        exitcode, _, _ = COMPILER[command_args] & TEE
        return exitcode

    update_project(command_args)
    run_info = PROJECT.compiler_extension(
        COMPILER, *command_args, project=PROJECT)

    return exit_code_from_run_infos(run_info)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
