"""
Test the SLURM script generator.
"""
import tempfile
import unittest
import unittest.mock

from plumbum import local

from benchbuild.experiments.empty import Empty
from benchbuild.projects.test import test
from benchbuild.utils import slurm
from benchbuild.utils.cmd import true


class TestSLURM(unittest.TestCase):

    def setUp(self):
        # Disable database interaction.
        test.TestProject.__attrs_post_init__ = unittest.mock.MagicMock()

        self.exp = Empty()
        self.prj = test.TestProject()
        self.tmp_file = local.path(tempfile.mktemp())

    def tearDown(self):
        self.tmp_file.delete()

    def test_script(self):
        script_path = local.path(
            slurm.__save__(self.tmp_file, true, self.exp, [self.prj]))

        self.assertTrue(self.tmp_file == script_path,
                        msg="Generated file does not match temporary file.")
        self.assertTrue(slurm.__verify__(self.tmp_file),
                        msg="Syntax check failed.")
