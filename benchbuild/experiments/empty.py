"""
The 'empty' Experiment.

This experiment is for debugging purposes. It only prepares the basic
directories for benchbuild. No compilation & no run can be done with it.
"""

from benchbuild.experiment import Experiment
from benchbuild.utils.actions import Download, Configure, MakeBuildDir, Clean


class Empty(Experiment):
    """The empty experiment."""

    NAME = "empty"

    def actions_for_project(self, project):
        """ Do nothing. """
        return [
            MakeBuildDir(project),
            Download(project),
            Configure(project),
            Clean(project)
        ]
