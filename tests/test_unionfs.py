""" Testing suite for the mounting process. """

import tempfile
import unittest

from plumbum import local

from benchbuild.settings import CFG

__UNIONFS_ENABLED__ = bool(CFG['unionfs']['enable'])


@unittest.skipIf(not __UNIONFS_ENABLED__, "Requires UnionFS to be enabled.")
class TestUnionFsMount(unittest.TestCase):
    """
    Class to test the mounting of the unionfs with different paths and check if
    the unmounting works without working with a whole filesystem yet.
    """

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir = local.path(tempfile.mkdtemp())
        print(cls.tmp_dir)

    @classmethod
    def tearDownClass(cls):
        if cls.tmp_dir.exists():
            cls.tmp_dir.delete()

    def test_build_dir(self):
        """ Check if the needed build_dir exists. """
        build_dir = local.path(str(CFG['build_dir']))
        self.assertTrue(build_dir.exists())


if __name__ == 'main':
    unittest.main()
