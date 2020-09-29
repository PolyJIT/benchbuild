"""
Test YAML functions from benchbuild's settings module.
"""
import unittest
import uuid

import yaml

from benchbuild.utils.settings import (
    uuid_add_implicit_resolver,
    uuid_constructor,
    uuid_representer,
)


class FakeLoader(yaml.SafeLoader):
    """FaketLoader for unit-testing."""
    pass


class FakeDumper(yaml.SafeDumper):
    """FakeDumper for unit-testing."""
    pass


TEST_UUID = 'cc3702ca-699a-4aa6-8226-4c938f294d9b'
EXPECTED_UUID_OBJ = {'test': uuid.UUID(TEST_UUID)}
EXPECTED_UUID_SCALAR = "test: !uuid 'cc3702ca-699a-4aa6-8226-4c938f294d9b'\n"
UUID_SCALAR = "{{'test': !uuid '{uuid}'}}".format(uuid=TEST_UUID)
UUID_OUT = "{{test: {uuid}}}".format(uuid=TEST_UUID)


class TestUUID(unittest.TestCase):
    """Test load and store of uuids inside Configuration objects."""

    def test_uuid_resolver(self):
        """Test dump and load of uuid objects."""

        uuid_in = {'test': uuid.UUID(TEST_UUID)}

        yaml.add_representer(uuid.UUID, uuid_representer, Dumper=FakeDumper)
        uuid_add_implicit_resolver(loader=FakeLoader, dumper=FakeDumper)

        self.assertEqual(
            yaml.dump(uuid_in, Dumper=FakeDumper),
            'test: cc3702ca-699a-4aa6-8226-4c938f294d9b\n'
        )
        self.assertEqual(
            yaml.load(UUID_OUT, Loader=FakeLoader), EXPECTED_UUID_OBJ
        )

    def test_uuid_construction(self):
        """Test uuid construction from scalar YAML nodes."""

        yaml.add_constructor("!uuid", uuid_constructor, Loader=yaml.SafeLoader)
        self.assertEqual(yaml.safe_load(UUID_SCALAR), EXPECTED_UUID_OBJ)

    def test_uuid_representer(self):
        """Test uuid representation as a scalar YAML node."""

        yaml.add_representer(
            uuid.UUID, uuid_representer, Dumper=yaml.SafeDumper
        )
        self.assertEqual(
            yaml.safe_dump(EXPECTED_UUID_OBJ), EXPECTED_UUID_SCALAR
        )
