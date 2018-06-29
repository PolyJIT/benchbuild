"""
Test the SLURM script generator.
"""
import os
import unittest
import tempfile
from unittest.mock import MagicMock
from plumbum.cmd import true
from benchbuild.experiments.empty import Empty
from benchbuild.projects.test.test import TestProject as Project
from benchbuild.utils.slurm import dump_slurm_script, verify_slurm_script


class TestSLURM(unittest.TestCase):
    def setUp(self):
        # Disable database interaction.
        Project.__attrs_post_init__ = MagicMock()

        self.exp = Empty()
        self.prj = Project(self.exp)
        self.tmp_file = tempfile.mktemp()

    def tearDown(self):
        os.remove(self.tmp_file)

    def test_dump_slurm_script(self):
        dump_slurm_script(self.tmp_file, true, self.exp, [self.prj])
        self.assertTrue(
            verify_slurm_script(self.tmp_file), msg="Syntax check failed.")
