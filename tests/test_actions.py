"""
Test the actions module.
"""
import unittest

from plumbum import ProcessExecutionError

from benchbuild.experiment import Experiment
from benchbuild.project import Project
from benchbuild.utils import actions as a


class EmptyProject(Project):
    NAME = "test_empty"
    DOMAIN = "debug"
    GROUP = "debug"
    SRC_FILE = "none"

    def build(self):
        pass

    def configure(self):
        pass

    def download(self):
        pass


class EmptyExperiment(Experiment):
    NAME = "test_empty"

    def actions_for_project(self, project):
        del project
        pass


class FailAlways(a.Step):

    def __call__(self):
        raise ProcessExecutionError([], 1, "", "")


class PassAlways(a.Step):

    def __call__(self):
        return a.StepResult.OK


class ActionsTestCase(unittest.TestCase):

    def test_for_all_pass(self):
        ep = EmptyProject(EmptyExperiment())
        actn = a.RequireAll(actions=[PassAlways(ep)])
        self.assertEqual(actn(), [a.StepResult.OK])

    def test_for_all_fail(self):
        ep = EmptyProject(EmptyExperiment())
        actn = a.RequireAll(actions=[FailAlways(ep)])
        self.assertEqual(actn(), [a.StepResult.ERROR])
