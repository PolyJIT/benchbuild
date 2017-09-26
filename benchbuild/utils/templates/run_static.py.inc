#!{{ python|default("/usr/bin/env python3") }}
#
import logging
import sys

from benchbuild.utils import log
from benchbuild.utils.run import exit_code_from_run_infos
from benchbuild.utils.wrapping import unpickle
from benchbuild import settings
from plumbum import local, TEE


LOG = logging.getLogger(__name__)


def main(argv):
    settings.update_env()
    log.configure()
    log.set_defaults()

    real_command = local["{{ runf }}"]
    real_command_args = argv[1:]

    with local.env(PATH="{{ path }}",
                   LD_LIBRARY_PATH="{{ ld_library_path }}",
                   BB_CMD=str(real_command) + " ".join(real_command_args)):
        blob_cmd = unpickle("{{ blobf }}")
        if blob_cmd is None:
            exitcode, _, _ = real_command[real_command_args] & TEE
            return exitcode

        run_info = blob_cmd(real_command, real_command_args)
        return exit_code_from_run_infos(run_info)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
