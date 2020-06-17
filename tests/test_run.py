"""
This Test will run through benchbuild's execution pipeline.
"""
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
