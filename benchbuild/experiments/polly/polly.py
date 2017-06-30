"""
The 'polly' Experiment
====================

This experiment applies polly's transformations to all projects and measures
the runtime.

This forms the baseline numbers for the other experiments.


Measurements
------------

3 Metrics are generated during this experiment:
    time.user_s - The time spent in user space in seconds (aka virtual time)
    time.system_s - The time spent in kernel space in seconds (aka system time)
    time.real_s - The time spent overall in seconds (aka Wall clock)
"""

from benchbuild.experiment import RuntimeExperiment
from benchbuild.extensions import RunWithTime, RuntimeExtension
from benchbuild.settings import CFG


class Polly(RuntimeExperiment):
    """The polly experiment."""

    NAME = "polly"

    def actions_for_project(self, project):
        """Compile & Run the experiment with -O3 enabled."""
        project.cflags = ["-O3", "-fno-omit-frame-pointer",
                          "-Xclang", "-load",
                          "-mllvm", "-stats",
                          "-Xclang", "LLVMPolly.so",
                          "-mllvm", "-polly"]
        project.runtime_extension = \
            RunWithTime(
                RuntimeExtension(project, self,
                                 {'jobs': int(CFG["jobs"].value())}))

        return self.default_runtime_actions(project)
