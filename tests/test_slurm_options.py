"""
Test the SLURM options generator.
"""
import os
import tempfile
import unittest
import unittest.mock

from plumbum import local

from benchbuild.experiments.empty import Empty
from benchbuild.projects.test import test
from benchbuild.utils import slurm
from benchbuild.utils.cmd import true
import benchbuild.utils.slurm_options as sopt


class TestSlurmOptions(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_script(self):
        pass


class TestCoresPerSocket(unittest.TestCase):
    """
    Checks if the CoresPerSocket option works correctly.
    """
    def test_init_cores(self):
        """
        Checks that we can correctly initialize a CoresPerSocket option.
        """
        option = sopt.CoresPerSocket(42)

        self.assertEqual(option.cores, 42)

    def test_merge_requirements(self):
        """
        Checks if cores per socket options are correctly merged together.
        """
        option = sopt.CoresPerSocket(4)
        other_option = sopt.CoresPerSocket(8)

        merged_option = sopt.CoresPerSocket.merge_requirements(
            option, other_option)
        merged_option_swapped = sopt.CoresPerSocket.merge_requirements(
            other_option, option)

        self.assertEqual(merged_option.cores, 8)
        self.assertEqual(merged_option_swapped.cores, 8)


class TestSlurmOptionMerger(unittest.TestCase):
    """
    Checks if slurm option list get merged correctly.
    """
    def test_merge_same(self):
        """
        Checks that merging two lists with the same option merges the options.
        """
        opt_list_1 = [sopt.CoresPerSocket(4)]
        opt_list_2 = [sopt.CoresPerSocket(8)]

        merged_list = sopt.merge_slurm_options(opt_list_1, opt_list_2)

        self.assertEqual(len(merged_list), 1)
        self.assertEqual(type(merged_list[0]), sopt.CoresPerSocket)
        self.assertEqual(merged_list[0].cores, 8)
