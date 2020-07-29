"""
Test issue 213: Wrong error tracking for failed commands
"""
import unittest

import attr
from plumbum import ProcessExecutionError

from benchbuild import experiment
from benchbuild import project as prj
from benchbuild.source import nosource
from benchbuild.utils import actions as a
from benchbuild.utils import tasks


@attr.s
class Issue213a(a.Step):
    NAME = "Issue213a"
    DESCRIPTION = "Issue213a"

    @a.notify_step_begin_end
    def __call__(self):
        raise ProcessExecutionError([], 1, "", "")


@attr.s
class Issue213b(a.Step):
    NAME = "Issue213b"
    DESCRIPTION = "Issue213b"

    @a.notify_step_begin_end
    def __call__(self):
        return a.StepResult.ERROR


@attr.s
class EmptyProject(prj.Project):
    """An empty project that serves as an empty shell for testing."""

    NAME = "test_empty"
    DOMAIN = "debug"
    GROUP = "debug"
    SOURCE = [nosource()]

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


class TrackErrorsTestCase(unittest.TestCase):
    """Test issue #213."""

    def test_exception(self):
        plan = list(
            tasks.generate_plan({"test_exception": ExceptionExp}.values(),
                                {"test_empty": EmptyProject}.values()))
        self.assertEqual(len(plan),
                         1,
                         msg="The test plan must have a length of 1.")

        failed = tasks.execute_plan(plan)
        self.assertEqual(len(failed), 1, msg="One step must fail!")

    def test_error_state(self):
        plan = list(
            tasks.generate_plan({"test_error_state": ErrorStateExp}.values(),
                                {"test_empty": EmptyProject}.values()))
        self.assertEqual(len(plan),
                         1,
                         msg="The test plan must have a length of 1.")

        failed = tasks.execute_plan(plan)
        self.assertEqual(len(failed), 1, msg="One step must fail!")
