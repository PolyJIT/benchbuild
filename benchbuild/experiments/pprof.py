"""
The 'pprof' Experiment.

TODO Description
"""
import logging

from benchbuild.experiment import RuntimeExperiment
from benchbuild.utils.actions import (Prepare, Build, Download, Configure,
                                      Clean, MakeBuildDir, Run, Echo)
from benchbuild.utils.run import track_execution, fetch_time_output
from benchbuild.utils.db import persist_time, persist_config
from benchbuild.utils.cmd import time

from benchbuild.settings import CFG
from functools import partial
from plumbum import local


def Instrument(project, experiment, config, jobs, run_f, args, **kwargs):
    """
    Run the given binary wrapped with time.

    Args:
        project: The benchbuild project that has called us.
        experiment: The benchbuild experiment which we operate under.
        config: The benchbuild configuration we are running with.
        jobs: The number of cores we are allowed to use. This may differ
            from the actual amount of available cores, obey it.
            We should enforce this from the outside. However, at the moment we
            do not do this.
        run_f: The file we want to execute.
        args: List of arguments that should be passed to the wrapped binary.
        **kwargs: Dictionary with our keyword args. We support the following
            entries:

            project_name: The real name of our project. This might not
                be the same as the configured project name, if we got wrapped
                with ::benchbuild.project.wrap_dynamic
            has_stdin: Signals whether we should take care of stdin.
            may_wrap:
                Project may signal that if they are not suitable for
                wrapping. Usually because they scan/parse the output, which
                may interfere with the output of the wrapper binary.
    """
    CFG.update(config)

    print("HERE")

    return

class RawRuntime(RuntimeExperiment):
    """The pprof experiment."""

    NAME = "pprof"

    def actions_for_project(self, project):
        """Compile & Run the experiment with -O3 enabled."""
        project.cflags = ["-O3", "-fno-omit-frame-pointer"]
        project.runtime_extension = partial(Instrument, project, self, CFG, CFG["jobs"].value())
        actns = [
            MakeBuildDir(project),
            Echo("Compiling... {}".format(project.name)),
            Prepare(project),
            Download(project),
            Configure(project),
            Build(project),
            Echo("Running... {}".format(project.name)),
            Run(project),
            Clean(project),
        ]
        return actns
