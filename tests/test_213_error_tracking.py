"""
Test issue 213: Wrong error tracking for failed commands
"""
import attr
import unittest
import logging

from plumbum import ProcessExecutionError

from benchbuild import project
from benchbuild import experiment
from benchbuild.utils import actions as a
from benchbuild.utils import tasks


@attr.s
class Issue213a(a.Step):
    @a.notify_step_begin_end
    def __call__(self):
        raise ProcessExecutionError([], 1, "", "")


@attr.s
class Issue213b(a.Step):
    @a.notify_step_begin_end
    def __call__(self):
        return a.StepResult.ERROR


class EmptyProject(project.Project):
    NAME = "test_empty"
    DOMAIN = "debug"
    GROUP = "debug"
    SRC_FILE = "none"

    def compile(self):
        pass

    def configure(self):
        pass


@attr.s
class ExceptionExp(experiment.Experiment):
    NAME = "test_exception"

    def actions_for_project(self, project):
        return [Issue213a(obj=project)]


@attr.s
class ErrorStateExp(experiment.Experiment):
    NAME = "test_error_state"

    def actions_for_project(self, project):
        return [Issue213b(obj=project)]


LOG = logging.getLogger(__name__)

class TrackErrorsTestCase(unittest.TestCase):
    def test_exception(self):
        plan = list(
            tasks.generate_plan({"test_exception": ExceptionExp},
                                {"test_empty": EmptyProject}))
        self.assertEqual(len(plan),
                         1,
                         msg="The test plan must have a length of 1.")

        failed = tasks.execute_plan(plan)
        self.assertEqual(len(failed), 1, msg="One step must fail!")

    def test_error_state(self):
        plan = list(
            tasks.generate_plan({"test_error_state": ErrorStateExp},
                                {"test_empty": EmptyProject}))
        self.assertEqual(len(plan),
                         1,
                         msg="The test plan must have a length of 1.")

        failed = tasks.execute_plan(plan)
        self.assertEqual(len(failed), 1, msg="One step must fail!")
