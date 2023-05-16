#!{{ python|default("/usr/bin/env python3") }}
#
import os
import re
import sys

from plumbum import TEE, local

{% if collect_coverage %}
import coverage
{% endif %}

# Performance optimization for benchbuild: don't import any experiments or
# projects. Everything necessary should be imported when loading (unpickling)
# the project.
os.environ["BB_PLUGINS_AUTOLOAD"] = "False"

from benchbuild.utils import log
from benchbuild.utils.db import persist_project
from benchbuild.utils.run import exit_code_from_run_infos
from benchbuild.utils.wrapping import load

PROJECT = load("{{ project_file }}")
FILTER_EXPRESSIONS = {{name_filters}}


def main(argv):
    log.configure()
    log.set_defaults()

    assert len(argv) >= 2, "2 or more arguments needed for the wrapper!"

    run_f = argv[1]
    real_command = local[run_f]
    real_command_args = argv[2:]

    PROJECT.name = os.path.basename(run_f)
    if FILTER_EXPRESSIONS:
        for name_filter in FILTER_EXPRESSIONS:
            match = re.match(name_filter, PROJECT.name)
            if match:
                PROJECT.name = match.group('name')
    persist_project(PROJECT)

    with local.env(
            PATH="{{ path }}",
            LD_LIBRARY_PATH="{{ ld_lib_path }}",
            HOME="{{ home }}",
            BB_CMD=str(real_command) + " ".join(real_command_args)):
        if PROJECT.runtime_extension is None:
            exitcode, _, _ = real_command[real_command_args] & TEE
            return exitcode

        run_info = PROJECT.runtime_extension(
            real_command, real_command_args, project=PROJECT)
        return exit_code_from_run_infos(run_info)


if __name__ == "__main__":
{% if collect_coverage %}
    cov = coverage.Coverage(
      config_file="{{ coverage_config }}",
      data_file="{{ coverage_path }}/.coverage",
      data_suffix=True,
      branch=True
    )
    cov.start()
{% endif %}
    ret = main(sys.argv)
{% if collect_coverage %}
    cov.stop()
    cov.save()
{% endif %}
    sys.exit(ret)
