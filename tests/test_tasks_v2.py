import unittest

from benchbuild.tasks import actions as a
from benchbuild.experiments.empty import Empty
from benchbuild.utils.actions import StepResult


class TestTaskGroups(unittest.TestCase):
    def test_has_owner_in_continue(self):
        task = a.echo("")
        grp = a.continue_group(task)

        self.assertEqual(task.owner, grp)

    def test_has_owner_in_fail(self):
        task = a.echo("")
        grp = a.fail_group(task)

        self.assertEqual(task.owner, grp)


    def test_plan(self):
        plan = a.continue_group(
            a.fail_group(a.echo("Hello"), a.echo("World")),
            a.fail_group(a.echo("Task v2"), a.echo("Task Test")))

        mgr = a.TaskManager(name="test", description="test", plan=plan)
        results = mgr.run()
        self.assertEqual(results, [StepResult.OK] * 4)

    def test_experiment(self):
        exp = a.manage_experiment(
            Empty(), a.fail_group(a.echo("hi from inside experiment")))
        results = exp.run()

        self.assertEqual(results, [StepResult.OK] * 3)

    def test_continue_on_fail(self):
        fail_t = a.Task("fail", "", lambda: StepResult.ERROR)
        plan = a.continue_group(fail_t, a.echo("after fail"))
        mgr = a.TaskManager("test continue on fail", "", plan=plan)
        results = mgr.run()

        self.assertEqual(len(results), 2, "Both actions have been executed")
        self.assertEqual(results, [StepResult.ERROR, StepResult.OK])

    def test_fail_on_first(self):
        fail_t = a.Task("fail", "", lambda: StepResult.ERROR)
        plan = a.fail_group(fail_t, a.echo("after fail"))
        mgr = a.TaskManager("test fail on first", "", plan=plan)
        results = mgr.run()

        self.assertEqual(len(results), 2,
                         "Both actions executed")
        self.assertEqual(results, [StepResult.ERROR, StepResult.ERROR], "no action executed succesfully")

    def test_continue_on_fail_2(self):
        fail_t = a.Task("fail", "", lambda: StepResult.ERROR)
        plan = a.continue_group(a.echo("before fail"), fail_t,
                                a.echo("after fail"))
        mgr = a.TaskManager("test continue on fail", "", plan=plan)
        results = mgr.run()

        self.assertEqual(len(results), 3, "All 3 actions have been executed")
        self.assertEqual(results,
                         [StepResult.OK, StepResult.ERROR, StepResult.OK])

    def test_fail_on_first_2(self):
        fail_t = a.Task("fail", "", lambda: StepResult.ERROR)
        plan = a.fail_group(a.echo("before fail"), fail_t,
                            a.echo("after fail"))
        mgr = a.TaskManager("test continue on fail", "", plan=plan)
        results = mgr.run()

        self.assertEqual(len(results), 3,
                         "2 out of 3 actions executed, but 3 returns")
        self.assertEqual(results, [StepResult.OK, StepResult.ERROR, StepResult.ERROR])
