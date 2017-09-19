#!{python}
#
from os import path
import logging
import sys
import dill

from benchbuild.utils import log
from benchbuild.utils.run import exit_code_from_run_infos
from benchbuild import settings
from plumbum import local, TEE


LOG = logging.getLogger(__name__)


def main(argv):
    settings.update_env()
    log.configure()
    log.set_defaults()

    real_command = local["{runf}"]
    real_command_args = sys.argv[1:]

    with local.env(PATH="{path}",
                   LD_LIBRARY_PATH="{ld_lib_path}",
                   BB_CMD=str(real_command) + " ".join(real_command_args)):
        if not path.exists("{blobf}"):
            LOG.info("No measurement blob found at %s", "{blobf}")
            exitcode, _, _ = real_command[real_command_args] & TEE
            return exitcode

        measurement_function = None
        with open("{blobf}", "rb") as p:
            measurement_function = dill.load(p)

        if measurement_function:
            run_info = measurement_function(
                real_command,
                real_command_args)
            return exit_code_from_run_infos(run_info)

        LOG.error("Unable to load measurement blob %s", "{blobf}")
        exitcode, _, _ = real_command[real_command_args] & TEE
        return exitcode


if __name__ == "__main__":
    sys.exit(main(sys.argv))
