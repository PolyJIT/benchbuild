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
import copy
import uuid

from benchbuild.experiment import RuntimeExperiment
from benchbuild.extensions import RunWithTime, RuntimeExtension
from benchbuild.settings import CFG


class PollyOpenMP(RuntimeExperiment):
    """Timing experiment with Polly & OpenMP support."""

    NAME = "polly-openmp"

    def actions_for_project(self, p):
        """Build & Run each project with Polly & OpenMP support."""
        actns = []

        p.ldflags = ["-lgomp"]
        p.cflags = ["-O3", "-Xclang", "-load", "-Xclang", "LLVMPolly.so",
                    "-mllvm", "-polly", "-mllvm", "-polly-parallel"]

        for i in range(2, int(str(CFG["jobs"])) + 1):
            cp = copy.deepcopy(p)
            cp.run_uuid = uuid.uuid4()
            cp.runtime_extension = \
                RunWithTime(
                    RuntimeExtension(p, self, {'jobs': i}))
            actns.extend(self.default_runtime_actions(cp))

        return actns
