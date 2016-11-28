""" Testing suite for the mounting process. """

import unittest
import os
from benchbuild.project import Project
from benchbuild.utils.container import get_base_dir
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import unionfs
from benchbuild.settings import CFG
from benchbuild.utils.cmd import ls


class TestProject(Project):
    """
    Class to get a self pointer for the project that is tested.
    The project also gets wrapped inside the unionfs.
    """

    #adjust parameters in the unionfs call to test different mounts
    @unionfs('./base', './image', None, './union')
    def mount_test_helper(self):
        """
        A plumbum or benchbuild command is called inside the wrapped unionfs and
        therefor also inside the mount as testing process.
        """

        self.run(ls)

    @classmethod
    def download(self):
        """ Get the project source input. """
        if self.NAME is not None:
            Wget(None, self.NAME) #None instead of Src_url just temporary

    @classmethod
    def configure(self):
        """ Configure the parameters of the project. """
        pass

    @classmethod
    def build(self):
        """ Build the project. """
        self.download()
        self.configure()

class TestUnionFsMount(unittest.TestCase):
    """
    Class to test the mounting of the unionfs with different paths and check if
    the unmounting works without working with a whole filesystem yet.
    """

    #mount_test_helper() to be integrated

    def test_mount_type(self):
        """ Tests if the mounting process encountered incorrect types. """
        self.assertRaises(TypeError)

    def test_path(self):
        """ Tests if the mount is at the expected path. """
        self.assertEqual(CFG["unionfs"]["base_dir"].value(), get_base_dir())

    def test_correct_unmount(self):
        """ Tests if the tear down of the mount was successfull. """
        self.assertFalse(os.path.exists(CFG["build_dir"].value()))
#both correct_ tests fail because they are currently
#checking for directorys that remain after the tear down.
#solution: test the functions concerning the mounts in utils/run.py seperatly
    def test_correct_cleanup(self):
        """ Tests if the clean up after the unmounting was successfull. """
        self.assertFalse(os.path.exists(CFG["unionfs"]["base_dir"].value()))

if __name__ == 'main':
    unittest.main(verbosity=2)
