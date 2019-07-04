import unittest

from benchbuild.tasks.actions import (continue_group, echo, fail_group,
                                      TaskManager, manage_experiment)
from benchbuild.experiments.empty import Empty
from benchbuild.utils.actions import StepResult


class TestPlan(unittest.TestCase):

    def test_plan(self):
        plan = continue_group(fail_group(echo("Hello"), echo("World")),
                              fail_group(echo("Task v2"), echo("Task Test")))

        mgr = TaskManager(name="test", description="test", plan=plan)
        results = mgr.run()
        self.assertEqual(
            results,
            [StepResult.OK] * 4)

    def test_experiment(self):
        exp = manage_experiment(
            Empty(), fail_group(
                echo("hi from inside experiment")))
        results = exp.run()

        self.assertEqual(results, [StepResult.OK] * 3)
