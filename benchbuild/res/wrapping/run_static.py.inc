#!{{ python|default("/usr/bin/env python3") }}
#
import sys

from plumbum import TEE, local

from benchbuild.utils import log
from benchbuild.utils.run import exit_code_from_run_infos
from benchbuild.utils.wrapping import load

PROJECT = load("{{ project_file }}")


def main(argv):
    log.configure()
    log.set_defaults()

    real_command = local["{{ runf }}"]
    real_command_args = argv[1:]

    with local.env(
            PATH="{{ path }}",
            LD_LIBRARY_PATH="{{ ld_library_path }}",
            HOME="{{ home }}",
            BB_CMD=str(real_command) + " ".join(real_command_args)):
        if PROJECT.runtime_extension is None:
            exitcode, _, _ = real_command[real_command_args] & TEE
            return exitcode

        run_info = PROJECT.runtime_extension(real_command, real_command_args)
        return exit_code_from_run_infos(run_info)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
