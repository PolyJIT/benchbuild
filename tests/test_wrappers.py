"""Test benchbuild's runtime wrappers."""
import tempfile
import unittest
import os


from plumbum import local
from plumbum.cmd import rm

from benchbuild.downloads.base import nosource

import benchbuild.experiments.empty as empty
import benchbuild.project as project
import benchbuild.utils.compiler as compilers
import benchbuild.utils.wrapping as wrappers


class EmptyProject(project.Project):
    NAME: str = "test_empty"
    DOMAIN: str = "debug"
    GROUP: str = "debug"
    SOURCE = [nosource()]

    def __attrs_post_init__(self):
        pass

    def build(self):
        pass

    def configure(self):
        pass

    def download(self):
        pass


class WrapperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp_dir = tempfile.mkdtemp()
        print(cls.tmp_dir)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.tmp_dir):
            rm("-r", cls.tmp_dir)

    def setUp(self):
        self.tmp_script_fd, self.tmp_script = tempfile.mkstemp(
            dir=self.tmp_dir)
        self.assertTrue(os.path.exists(self.tmp_script))


class RunCompiler(WrapperTests):
    def test_create(self):
        with local.cwd(self.tmp_dir):
            cmd = compilers.cc(EmptyProject(empty.Empty()))
        self.assertTrue(os.path.exists(str(cmd)))


class RunStatic(WrapperTests):
    def test_create(self):
        with local.cwd(self.tmp_dir):
            self.cmd = wrappers.wrap(self.tmp_script,
                                     EmptyProject(empty.Empty()))
            self.assertTrue(os.path.exists("{}.bin".format(self.tmp_script)))
        self.assertTrue(os.path.exists(str(self.cmd)))


class RunDynamic(WrapperTests):
    def test_create(self):
        with local.cwd(self.tmp_dir):
            cmd = wrappers.wrap_dynamic(
                EmptyProject(empty.Empty()), self.tmp_script)
        self.assertTrue(os.path.exists(str(cmd)))
