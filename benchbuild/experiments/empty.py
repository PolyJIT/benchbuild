"""
The 'empty' Experiment.

This experiment is for debugging purposes. It only prepares the basic
directories for benchbuild. No compilation & no run can be done with it.
"""

from benchbuild.experiment import Experiment
from benchbuild.extensions import compiler, run
from benchbuild.utils.actions import Clean, Compile, MakeBuildDir


class Empty(Experiment):
    """The empty experiment."""

    NAME = "empty"

    def actions_for_project(self, project):
        """ Do nothing. """
        project.compiler_extension = run.WithTimeout(
            compiler.RunCompiler(project, self))
        return [MakeBuildDir(project), Compile(project), Clean(project)]


class NoMeasurement(Experiment):
    """Run everything but do not measure anything."""

    NAME = "no-measurement"

    def actions_for_project(self, project):
        """Execute all actions but don't do anything as extension."""
        project.compiler_extension = run.WithTimeout(
            compiler.RunCompiler(project, self))
        project.runtime_extension = run.RuntimeExtension(project, self)
        return self.default_runtime_actions(project)
