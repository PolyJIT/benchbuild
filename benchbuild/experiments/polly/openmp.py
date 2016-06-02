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

from benchbuild.experiment import step, RuntimeExperiment
from benchbuild.settings import CFG


class PollyOpenMP(RuntimeExperiment):
    """Timing experiment with Polly & OpenMP support."""

    NAME = "polly-openmp"

    def run_project(self, p):
        """Build & Run each project with Polly & OpenMP support."""
        from uuid import uuid4
        from benchbuild.experiments.raw import run_with_time
        from benchbuild.utils.run import partial

        p.ldflags = ["-lgomp"]
        p.cflags = ["-O3", "-Xclang", "-load", "-Xclang", "LLVMPolly.so",
                    "-mllvm", "-polly", "-mllvm", "-polly-parallel"]

        for i in range(1, int(CFG["jobs"]) + 1):
            p.run_uuid = uuid4()
            with step("time: {0} cores & uuid {1}".format(i, p.run_uuid)):
                p.clean()
                p.prepare()
                p.download()
                p.configure()
                p.build()
                p.run(partial(run_with_time, p, self, CFG, i))
