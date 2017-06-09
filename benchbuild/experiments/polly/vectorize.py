"""
The 'polly-vectorize' Experiment
====================

This experiment applies polly's transformations with stripmine vectorizer
enabled to all projects and measures the runtime.

This forms the baseline numbers for the other experiments.

Measurements
------------

3 Metrics are generated during this experiment:
    time.user_s - The time spent in user space in seconds (aka virtual time)
    time.system_s - The time spent in kernel space in seconds (aka system time)
    time.real_s - The time spent overall in seconds (aka Wall clock)
"""

from benchbuild.experiment import RuntimeExperiment
from benchbuild.experiments.raw import run_with_time
from benchbuild.utils.actions import (Prepare, Build, Download, Configure,
                                      Clean, MakeBuildDir, Run, Echo)
from benchbuild.settings import CFG
import functools


class PollyVectorizer(RuntimeExperiment):
    """ The polly experiment with vectorization enabled. """

    NAME = "polly-vectorize"

    def actions_for_project(self, project):
        """Compile & Run the experiment with -O3 enabled."""
        project.cflags = ["-O3", "-fno-omit-frame-pointer",
                          "-Xclang", "-load",
                          "-Xclang", "LLVMPolyJIT.so",
                          "-mllvm", "-polly",
                          "-mllvm", "-polly-vectorizer=stripmine"]
        project.runtime_extension = functools.partial(
            run_with_time, project, self, CFG, CFG["jobs"].value())
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
