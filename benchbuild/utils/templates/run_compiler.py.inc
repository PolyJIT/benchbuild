#!{{ python|default("/usr/bin/env python3") }}
#
import sys

from benchbuild.utils import log
from benchbuild.utils.run import exit_code_from_run_infos
from benchbuild.utils.wrapping import unpickle
from benchbuild import settings
from plumbum import TEE


CFLAGS = {{ cflags }}
LDFLAGS = {{ ldflags }}


def main(argv):
    settings.update_env()
    log.configure()
    log.set_defaults()

    command_args = argv[1:]
    cc_cmd = unpickle("{{ cc_f }}")
    if cc_cmd is None:
        sys.exit(1)

    blob_cmd = unpickle("{{ blob_f }}")
    if blob_cmd is None:
        exitcode, _, _ = cc_cmd[command_args] & TEE
        return exitcode

    run_info = blob_cmd(cc_cmd, *command_args,
                        experiment_cflags=CFLAGS,
                        experiment_ldflags=LDFLAGS)
    return exit_code_from_run_infos(run_info)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
