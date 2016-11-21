import unittest
from benchbuild.utils.run import unionfs
from benchbuild.project import Project


class TestProject(Project):
    """
    Class to get a self pointer for the project that is to be tested.
    The project also gets wrapped inside the unionfs.
    """

    @unionfs("""Adjust base_dir, image_dir etc.""")
    def mount_test_helper(self):
        """
        A plumbum or benchbuild command is called inside the wrapped unionfs and
        therefor also inside the mount as testing process.
        """
        from benchbuild.cmd import ls #or other plumbum/benchbuild commands

    def download(self):
        """Get the project that is needed and referenced."""
        pass

class TestUnionFsMount(unittest.TestCase):
    """
    Class to test the mounting of the unionfs with different paths and check if
    the unmounting works without working with the actual filesystem yet.
    """
    def test_foo(self):
        """The actual test of the mounting processes."""
        pass
