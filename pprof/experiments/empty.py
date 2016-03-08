"""
The 'empty' Experiment.

This experiment is for debugging purposes. It only prepares the basic
directories for pprof. No compilation & no run can be done with it.
"""

from pprof.experiment import Experiment


class Empty(Experiment):
    """The empty experiment."""

    NAME = "empty"

    def run_project(self, p):
        """ Do nothing. """
        p.download()
        p.configure()
        p.build()
        p.clean()
