#!{python}
#
import logging
import os
import sys
import dill

from benchbuild.project import Project
from benchbuild.utils import log
from benchbuild import settings
from benchbuild.experiment import Experiment
from benchbuild.utils.run import exit_code_from_run_infos

from plumbum import local, FG
from {base_module} import {base_class} as PBC


LOG = logging.getLogger(__name__)
LOG.setLevel(logging.ERROR)

EXPERIMENT_NAME = os.getenv("BB_EXPERIMENT", "unknown")
DOMAIN_NAME = os.getenv("BB_DOMAIN", PBC.DOMAIN)
GROUP_NAME = os.getenv("BB_GROUP", PBC.GROUP)


def main(argv):
    settings.update_env()
    log.configure()
    log.set_defaults()

    assert len(argv) >= 2, "2 or more arguments needed for the wrapper!"

    run_f = sys.argv[1]
    real_command = local[run_f]
    real_command_args = sys.argv[2:]
    project_name = os.path.basename(run_f)

    with local.env(PATH="{path}",
                   LD_LIBRARY_PATH="{ld_lib_path}",
                   BB_CMD=str(real_command) + " ".join(real_command_args)):
        if not os.path.exists("{blobf}"):
            LOG.info("No measurement blob found at %s", "{blobf}")
            exitcode, _, _ = real_command[real_command_args] & FG
            return exitcode

        measurement_function = None
        with open("{blobf}", "rb") as p:
            measurement_function = dill.load(p)

        if measurement_function:
            project_cls = type("Dyn_" + project_name, (PBC,), {{
                "NAME": project_name,
                "DOMAIN": DOMAIN_NAME,
                "GROUP": GROUP_NAME,
                "__module__": "__main__"
            }})

            experiment_cls = type(EXPERIMENT_NAME, (Experiment,), {{
                "NAME": EXPERIMENT_NAME
            }})

            e = experiment_cls([project_name], [GROUP_NAME])
            p = project_cls(e)

            run_info = measurement_function(
                real_command,
                real_command_args,
                project_name=project_name)
            return exit_code_from_run_infos(run_info)

        LOG.error("Unable to load measurement blob %s", "{blobf}")
        exitcode, _, _ = real_command[real_command_args] & FG
        return exitcode


if __name__ == "__main__":
    sys.exit(main(sys.argv))
