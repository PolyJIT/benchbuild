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
    from benchbuild.utils.run import uchroot_mounts, unionfs_set_up, \
        unionfs_tear_down

    build_dir = CFG["build_dir"].value()
    base_dir = CFG["unionfs"]["base_dir"].value()
    caller = TestProject(Project)
    TestProject.mount_test_helper(caller)

    def test_unionfs_set_up(self):
        """ Tests if the set up of the unionfs was successfull. """
        unionfs_set_up(get_base_dir(), CFG["tmp_dir"].value(), build_dir)
        self.assertRaises(ValueError)

    def test_mount_location(self):
        """ Tests if the mount is at the expected path. """
        self.assertEqual(base_dir, get_base_dir())

    def test_uchroot_mounts(self):
        """ Tests if the mountpoints of the chroot could be located. """
        expected_mountpoints = []
        self.assertEquals(expected_mountpoints, uchroot_mounts(
            build_dir, prefix=None))

    def test_unionfs_tear_down(self):
        """ Tests if the tear down of the unionfs was successfull. """
        unionfs_tear_down(build_dir, 3)
        self.assertRaises(ValueError)
        self.assertRaises(RuntimeError)
#normally you would not test multiple asserts with one test,
#but here the second one is never executed if the first one does not pass anyway

    def test_correct_cleanup(self):
        """ Tests if the clean up after the unmounting was successfull. """
        self.assertFalse(os.path.exists(base_dir))

if __name__ == 'main':
    unittest.main(verbosity=2)
