"""
Test the actions module.
"""
import unittest
from benchbuild.utils import actions as a
from benchbuild.project import Project
from benchbuild.experiment import Experiment
from plumbum import ProcessExecutionError

class EmptyProject(Project):
    NAME = "test_empty"
    DOMAIN = "debug"
    GROUP = "debug"

class EmptyExperiment(Experiment):
    NAME = "test_empty"

class FailAlways(a.Step):
    def __call__(self):
        raise ProcessExecutionError([], 1, "", "")

class PassAlways(a.Step):
    def __call__(self):
        return a.StepResult.OK

class ActionsTestCase(unittest.TestCase):
    def test_for_all_pass(self):
        ep = EmptyProject(EmptyExperiment())
        actn = a.ForAll([ PassAlways(ep) ])
        self.assertEqual(actn(), a.StepResult.OK)

    def test_for_all_fail(self):
        ep = EmptyProject(EmptyExperiment())
        actn = a.ForAll([ FailAlways(ep) ])
        self.assertEqual(actn(), a.StepResult.ERROR)
