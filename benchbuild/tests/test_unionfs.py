import unittest
from benchbuild.utils.run import unionfs
from benchbuild.project import Project


class TestProject(Project):
    """
    Class to get a self pointer for the project that is tested.
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
    import os
    from benchbuild.utils.container import get_path_of_container

    path = get_path_of_container()
    def test_mount_type(self):
        """Tests if the mounting process encountered incorrect types."""
        self.assertRaises(TypeError)

    def test_path(self, test_path):
        """Tests if the mount is at the expected path."""
        self.assertEqual(test_path, path)

    def test_correct_unmount(self):
        """Tests if the tear down of the mount was successfull."""
        self.assertFalse(os.path.exists(path))

    def test_correct_cleanup(self):
        """Tests if the clean up after the unmounting was successfull."""
        pass


if __name__ == 'main':
    unittest.main()
