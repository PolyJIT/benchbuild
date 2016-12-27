"""
The 'polly-openmp' Experiment.

This experiment applies polly's transformations with openmp code generation
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
from benchbuild.settings import CFG
from benchbuild.utils.actions import (Prepare, Build, Download, Configure,
                                      Clean, MakeBuildDir, Run, Echo)
import copy
import uuid


class PollyOpenMP(RuntimeExperiment):
    """Timing experiment with Polly & OpenMP support."""

    NAME = "polly-openmp"

    def actions_for_project(self, p):
        """Build & Run each project with Polly & OpenMP support."""
        from benchbuild.experiments.raw import run_with_time
        from functools import partial

        actns = []

        p.ldflags = ["-lgomp"]
        p.cflags = ["-O3", "-Xclang", "-load", "-Xclang", "LLVMPolly.so",
                    "-mllvm", "-polly", "-mllvm", "-polly-parallel"]

        for i in range(2, int(str(CFG["jobs"])) + 1):
            cp = copy.deepcopy(p)
            cp.run_uuid = uuid.uuid4()
            cp.runtime_extension = partial(run_with_time, cp, self, CFG, i)
            actns.extend([
                Echo("========= START: Polly (OpenMP) - Cores: {0}".format(i)),
                MakeBuildDir(cp),
                Prepare(cp),
                Download(cp),
                Configure(cp),
                Build(cp),
                Run(cp),
                Clean(cp),
                Echo("========= END: Polly (OpenMP) - Cores: {0}".format(i)),
            ])

        return actns
