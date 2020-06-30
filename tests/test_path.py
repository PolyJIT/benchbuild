import unittest


class TestPathToList(unittest.TestCase):

    def test_path_to_list(self):
        from benchbuild.utils.path import path_to_list
        p = path_to_list("a:b")
        self.assertEqual(p, ["a", "b"])

        p = path_to_list("a")
        self.assertEqual(p, ["a"])

        p = path_to_list("")
        self.assertEqual(p, [])

    def test_list_to_path(self):
        from benchbuild.utils.path import list_to_path
        p = list_to_path(["a", "b"])
        self.assertEqual(p, "a:b")

        p = list_to_path(["a"])
        self.assertEqual(p, "a")

        p = list_to_path([""])
        self.assertEqual(p, "")
