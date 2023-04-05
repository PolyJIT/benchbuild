#!{{ python|default("/usr/bin/env python3") }}
#
import os
import sys

{% if collect_coverage %}
import coverage
{% endif %}

from plumbum import TEE, local

# Performance optimization for benchbuild: don't import any experiments or
# projects. Everything necessary should be imported when loading (unpickling)
# the project.
os.environ["BB_PLUGINS_AUTOLOAD"] = "False"

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
