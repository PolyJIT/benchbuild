import unittest

from benchbuild.tasks.actions import (ContinueOnError, Echo, FailOnError,
                                      TaskManager, Experiment)
from benchbuild.experiments.empty import Empty
from benchbuild.utils.actions import StepResult


class TestPlan(unittest.TestCase):

    def test_plan(self):
        plan = ContinueOnError([
            FailOnError([Echo(message="Hello"),
                         Echo(message="World")]),
            FailOnError([Echo(message="Task v2"),
                         Echo(message="Task Test")])
        ])

        tm = TaskManager(plan=plan)
        results = tm.run()
        self.assertEqual(
            results,
            [StepResult.OK] * 4)

    def test_experiment(self):
        exp = Experiment(experiment=Empty(),
                         plan=ContinueOnError(
                             [Echo(message="Hi from inside experiment")]))
        tm = TaskManager(plan=exp)

        results = tm.run()

        self.assertEqual(results, [StepResult.OK] * 3)
