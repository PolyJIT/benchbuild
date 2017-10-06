#!{{ python|default("/usr/bin/env python3") }}
#
import logging
import os
import re
import sys

from benchbuild.utils import log
from benchbuild.utils.wrapping import unpickle
from benchbuild import settings
from benchbuild.experiment import Experiment
from benchbuild.utils.run import exit_code_from_run_infos

from plumbum import local, TEE
from {{ base_module }} import {{ base_class}} as PBC


LOG = logging.getLogger(__name__)


EXPERIMENT_NAME = os.getenv("BB_EXPERIMENT", "unknown")
DOMAIN_NAME = os.getenv("BB_DOMAIN", PBC.DOMAIN)
GROUP_NAME = os.getenv("BB_GROUP", PBC.GROUP)
FILTER_EXPRESSIONS = {{ name_filters }}

def main(argv):
    settings.update_env()
    log.configure()
    log.set_defaults()

    assert len(argv) >= 2, "2 or more arguments needed for the wrapper!"

    run_f = argv[1]
    real_command = local[run_f]
    real_command_args = argv[2:]
    project_name = os.path.basename(run_f)

    if FILTER_EXPRESSIONS:
        for name_filter in FILTER_EXPRESSIONS:
            match = re.match(name_filter, project_name)
            if match:
                project_name = match.group('name')

    with local.env(PATH="{{ path }}",
                   LD_LIBRARY_PATH="{{ ld_lib_path }}",
                   BB_CMD=str(real_command) + " ".join(real_command_args)):
        blob_cmd = unpickle("{{ blobf }}")
        if blob_cmd is None:
            exitcode, _, _ = real_command[real_command_args] & TEE
            return exitcode

        project_cls = type("Dyn_" + project_name, (PBC,), {
            "NAME": project_name,
            "DOMAIN": DOMAIN_NAME,
            "GROUP": GROUP_NAME,
            "__module__": "__main__"
        })

        experiment_cls = type(EXPERIMENT_NAME, (Experiment,), {
            "NAME": EXPERIMENT_NAME
        })

        project_cls(experiment_cls([project_name], [GROUP_NAME]))
        run_info = blob_cmd(
            real_command,
            real_command_args,
            project_name=project_name)
        return exit_code_from_run_infos(run_info)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
