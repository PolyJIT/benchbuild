"""
This Test will run through benchbuild's execution pipeline.
"""
import os
import unittest

from benchbuild.utils import cmd


def shadow_commands(command):

    def shadow_command_fun(func):

        def shadow_command_wrapped_fun(self, *args, **kwargs):
            cmd.__override_all__ = command
            res = func(self, *args, **kwargs)
            cmd.__override_all__ = None
            return res

        return shadow_command_wrapped_fun

    return shadow_command_fun


class TestShadow(unittest.TestCase):

    def test_shadow(self):
        inside = None
        true = cmd.true
        mkdir = cmd.mkdir

        class test_class(object):

            @shadow_commands("true")
            def shadow_hook(self):
                return cmd.mkdir

        outside = cmd.mkdir
        inside = test_class().shadow_hook()
        self.assertEqual(inside.formulate(),
                         true.formulate(),
                         msg="true (before) is not the same as true (inside)")
        self.assertNotEqual(
            mkdir.formulate(),
            inside.formulate(),
            msg="mkdir (before) is not the same as mkdir (inside)")
        self.assertNotEqual(inside.formulate(),
                            outside.formulate(),
                            msg="true (before) is not the same as true (after)")
        self.assertEqual(mkdir.formulate(),
                         outside.formulate(),
                         msg="mkdir (before) is not the same as mkdir (after)")


class TestRun(unittest.TestCase):

    @shadow_commands("true")
    def test_run(self):
        from benchbuild import experiment
        from benchbuild.utils.actions import Experiment

        class MockExp(experiment.Experiment):
            NAME = "mock-exp"

            def actions_for_project(self, project):
                from benchbuild.utils.actions import (Prepare, Download,
                                                      Configure, Build, Run,
                                                      Clean)
                actns = []
                project.builddir = "/tmp/throwaway"
                actns = [
                    Prepare(project),
                    Download(project),
                    Configure(project),
                    Build(project),
                    Run(project),
                    Clean(project)
                ]
                return actns

        exp = MockExp()
        eactn = Experiment(obj=exp, actions=exp.actions())
        old_exists = os.path.exists
        os.path.exists = lambda p: True
        print(eactn)
        eactn()
        os.path.exists = old_exists


if __name__ == "__main__":
    from benchbuild.utils import log
    log.configure()
    TestRun().test_run()
