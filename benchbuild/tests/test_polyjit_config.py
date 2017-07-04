"""
Test the PolyJITConfig objects.
"""
import unittest
from benchbuild.utils.dict import extend_as_list
from benchbuild.experiments.polyjit import EnablePolyJIT, DisablePolyJIT

class DictTestCase(unittest.TestCase):

    def test_set_value(self):
        a = EnablePolyJIT()

        with a.argv(PJIT_ARGS="-a"):
            self.assertEqual(a.argv['PJIT_ARGS'], "-a")
        self.assertNotIn('PJIT_ARGS', a.argv)

    def test_set_from_different_objects(self):
        a = EnablePolyJIT()
        b = DisablePolyJIT()

        with a.argv(PJIT_ARGS="-a"):
            self.assertIn('PJIT_ARGS', b.argv)
        self.assertNotIn('PJIT_ARGS', b.argv)

    def test_set_nested_from_different_objects(self):
        a = EnablePolyJIT()
        b = DisablePolyJIT()

        with a.argv(PJIT_ARGS="-a"):
            with b.argv(PJIT_ARGS="-b"):
                self.assertIn('PJIT_ARGS', b.argv)
                self.assertEqual(b.argv['PJIT_ARGS'], ["-a", "-b"])
        self.assertNotIn('PJIT_ARGS', b.argv)