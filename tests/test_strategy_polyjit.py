import unittest

from benchbuild.settings import CFG


class TestPolyJITPackages(unittest.TestCase):

    def test_package_defaults(self):
        packages = CFG["container"]["strategy"]["polyjit"]["packages"].value
        self.assertIsInstance(packages, list, msg="Not a list!")

    def test_package_atoms_name(self):
        packages = CFG["container"]["strategy"]["polyjit"]["packages"].value
        for pkg in packages:
            self.assertIn("name",
                          pkg,
                          msg="{0} lacks 'name' attribute".format(str(pkg)))

    def test_package_atoms_env(self):
        packages = CFG["container"]["strategy"]["polyjit"]["packages"].value
        for pkg in packages:
            self.assertIn("env",
                          pkg,
                          msg="{0} lacks 'env' attribute".format(str(pkg)))

    def test_package_atoms_use_is_list(self):
        packages = CFG["container"]["strategy"]["polyjit"]["packages"].value
        for pkg in packages:
            self.assertIsInstance(pkg["env"],
                                  dict,
                                  msg='"env" attribute is not a dict')

    def test_package_atoms_name_is_str(self):
        packages = CFG["container"]["strategy"]["polyjit"]["packages"].value
        for pkg in packages:
            self.assertIsInstance(pkg["name"],
                                  str,
                                  msg='"name" attribute is not a str')
