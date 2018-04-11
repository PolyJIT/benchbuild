""" Testing suite for the mounting process. """

import unittest
import os
from benchbuild.project import Project
from benchbuild.utils.downloader import Wget
from benchbuild.settings import CFG
from benchbuild.utils.cmd import ls


class ProjectMock(Project):
    """
    Class to get a self pointer for the project that is tested.
    The project also gets wrapped inside the unionfs.
    """
    from benchbuild.utils.run import unionfs

    @unionfs('./base', './image', None, './union')
    def mount_test_helper(self):
        """
        A plumbum or benchbuild command is called inside the wrapped unionfs
        and therefore also inside the mount, added manually here.
        The function wrapped with this helper is later on compared with the
        actual unionfs-wrapped function as a testing process.
        """

        self.build()
        self.run(ls)

    def download(self):
        """ Get the project source input. """
        Wget(self.src_url, self.NAME)

    def configure(self):
        """ Configure the parameters of the project. """
        pass

    def build(self):
        """ Build the project. """
        self.download()
        self.configure()


class TestUnionFsMount(unittest.TestCase):
    """
    Class to test the mounting of the unionfs with different paths and check if
    the unmounting works without working with a whole filesystem yet.
    """

    def test_build_dir(self):
        """ Check if the needed build_dir exists. """
        self.assertTrue(os.path.exists(CFG["build_dir"].value()))


if __name__ == 'main':
    unittest.main()
