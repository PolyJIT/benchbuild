""" Testing suite for the mounting process. """

import unittest
import os
from benchbuild.project import Project
from benchbuild.utils.container import get_base_dir
from benchbuild.utils.downloader import Wget
from benchbuild.settings import CFG
from benchbuild.utils.cmd import ls


class ProjectMock(Project):
    """
    Class to get a self pointer for the project that is tested.
    The project also gets wrapped inside the unionfs.
    """
    from benchbuild.utils.run import unionfs

    #adjust parameters in the unionfs call to test different mounts
    @unionfs('./base', './image', None, './union')
    def mount_test_helper(self):
        """
        A plumbum or benchbuild command is called inside the wrapped unionfs and
        therefor also inside the mount, added manually here.
        The function wrapped with this helper is later on compared with the
        actual unionfs-wrapped function as a testing process.
        """

        self.build()
        self.run(ls)

    @classmethod
    def download(self):
        """ Get the project source input. """
        Wget(self.sourcedir, self.NAME)

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

    def test_build_dir(self):
        """ Check if the needed build_dir exists. """
        self.assertTrue(os.path.exists(CFG["build_dir"].value()))

    def test_base_dir(self):
        """ Check if the needed base_dir exsists. """
        self.assertTrue(os.path.exists(get_base_dir()))

    def test_unionfs_wrapping(self):
        """ Tests if the wrapped unionfs returns a function. """
        #can not build a new TestProject-object as caller
        #also can not wrap a new unionfs around a non-funtion
        #call can not be assigned to just the call of the mount_test_helper

    def test_mount_location(self):
        """ Tests if the mount is at the expected path. """
        #settings do not save the base_dir yet, initialise an experiment first
        base_dir = CFG["unionfs"]["base_dir"].value()
        self.assertEqual(base_dir, get_base_dir())

    def test_unionfs_tear_down(self):
        """ Tests if the tear down of the unionfs was successfull. """
        from benchbuild.utils.run import unionfs_tear_down
        build_dir = CFG["build_dir"].value()
        unionfs_tear_down(build_dir, 3)
        self.assertRaises(ValueError)
        self.assertRaises(RuntimeError)
        #the second assert is never reached if the first one fails

if __name__ == 'main':
    unittest.main()
