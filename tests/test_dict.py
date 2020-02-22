"""
Test the dict module.
"""
import unittest

from benchbuild.utils.dict import ExtensibleDict as edict
from benchbuild.utils.dict import extend_as_list


class DictTestCase(unittest.TestCase):

    def test_store_value(self):
        a = edict()
        a['TEST'] = 0
        self.assertEqual(a['TEST'], 0)

    def test_nesting_storage(self):
        a = edict()
        a['TEST'] = 0
        with a(TEST=1):
            self.assertEqual(a['TEST'], 1)
        self.assertEqual(a['TEST'], 0)

    def test_extending_storage_single_element(self):
        a = edict()
        a['TEST'] = 0
        with a(extender_fn=extend_as_list, TEST=1):
            self.assertEqual(a['TEST'], [0, 1])
        self.assertEqual(a['TEST'], 0)

    def test_extending_storage_list_element(self):
        a = edict()
        a['TEST'] = 0
        with a(extender_fn=extend_as_list, TEST=[1, 2]):
            self.assertEqual(a['TEST'], [0, 1, 2])
        self.assertEqual(a['TEST'], 0)

    def test_default_extender_fn(self):
        a = edict(extend_as_list)
        a['TEST'] = 0
        with a(TEST=[1, 2]):
            self.assertEqual(a['TEST'], [0, 1, 2])
        self.assertEqual(a['TEST'], 0)

    def test_non_existing_key(self):
        b = edict(extend_as_list)
        b.clear()
        with b(TEST=[1, 2]):
            self.assertEqual(b['TEST'], [1, 2])
        self.assertNotIn('TEST', b)
