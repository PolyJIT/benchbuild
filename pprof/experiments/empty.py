"""
The 'empty' Experiment.

This experiment is for debugging purposes. It only prepares the basic
directories for pprof. No compilation & no run can be done with it.
"""

from pprof.experiment import Experiment
from pprof.utils.actions import Download, Configure, Build, MakeBuildDir, Clean


class Empty(Experiment):
    """The empty experiment."""

    NAME = "empty"

    def actions_for_project(self, p):
        """ Do nothing. """
        return [
            MakeBuildDir(p),
            Download(p),
            Configure(p),
            Build(p),
            Clean(p)
        ]
