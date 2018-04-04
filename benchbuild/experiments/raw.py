"""
The 'raw' Experiment.

This experiment is the basic experiment in the benchbuild study. It simply runs
all projects after compiling it with -O3. The binaries are wrapped
with the time command and results are written to the database.

This forms the baseline numbers for the other experiments.

Measurements
------------

3 Metrics are generated during this experiment:
    time.user_s - The time spent in user space in seconds (aka virtual time)
    time.system_s - The time spent in kernel space in seconds (aka system time)
    time.real_s - The time spent overall in seconds (aka Wall clock)
"""
from benchbuild.experiment import Experiment
from benchbuild.extensions import RunWithTime, RuntimeExtension


class RawRuntime(Experiment):
    """The polyjit experiment."""

    NAME = "raw"

    def actions_for_project(self, project):
        """Compile & Run the experiment with -O3 enabled."""
        project.cflags = ["-O3", "-fno-omit-frame-pointer"]
        project.runtime_extension = RunWithTime(
            RuntimeExtension(project, self))
        return self.default_runtime_actions(project)
