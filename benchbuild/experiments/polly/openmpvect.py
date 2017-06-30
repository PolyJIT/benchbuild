"""
The 'polly-openmp-vectorize' Experiment.

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
from benchbuild.extensions import RunWithTime, RuntimeExtension
from benchbuild.settings import CFG


class PollyOpenMPVectorizer(RuntimeExperiment):
    """Timing experiment with Polly & OpenMP+Vectorizer support."""

    NAME = "polly-openmpvect"

    def actions_for_project(self, project):
        """Compile & Run the experiment with -O3 enabled."""
        project.cflags = ["-O3", "-fno-omit-frame-pointer",
                          "-Xclang", "-load",
                          "-Xclang", "LLVMPolly.so",
                          "-mllvm", "-polly",
                          "-mllvm", "-polly-parallel",
                          "-mllvm", "-polly-vectorizer=stripmine"]
        project.ldflags = ["-lgomp"]
        project.runtime_extension = \
            RunWithTime(
                RuntimeExtension(project, self,
                                 {'jobs': int(CFG["jobs"].value())}))

        return self.default_runtime_actions(project)
