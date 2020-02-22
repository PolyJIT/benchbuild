"""
Test path creation functions from benchbuild's settings module.
"""
import pathlib
import unittest

import pytest
import yaml

from benchbuild.utils.settings import (ConfigPath, path_constructor,
                                       path_representer)

TEST_PATH = '/tmp/test/foo'
TEST_PATH_OBJ = "{'test': !create-if-needed '/tmp/test/foo'}"
EXPECTED_PATH_YAML = "test: !create-if-needed '/tmp/test/foo'\n"
EXPECTED_CONFIG_PATH = {'test': ConfigPath('/tmp/test/foo')}


@pytest.fixture
def rm_test_path():
    yield
    p = pathlib.Path(TEST_PATH)
    p.rmdir()


def test_root_path():
    """Test root path construction."""
    assert str(ConfigPath([])) == '/'


def test_simple_path():
    """Test simple path construction."""
    assert str(ConfigPath(['tmp'])) == '/tmp'


def test_nested_path():
    """Test nested path construction."""
    assert str(ConfigPath(str(TEST_PATH))) == '/tmp/test/foo'


def test_construct():
    """Test path construction from YAML."""
    yaml.add_constructor("!create-if-needed",
                         path_constructor,
                         Loader=yaml.SafeLoader)

    assert yaml.safe_load(TEST_PATH_OBJ) == EXPECTED_CONFIG_PATH


def test_represent():
    """Test scalar representation."""
    yaml.add_representer(ConfigPath, path_representer, Dumper=yaml.SafeDumper)
    assert yaml.safe_dump(EXPECTED_CONFIG_PATH) == EXPECTED_PATH_YAML


def test_path_validation(capsys, rm_test_path):
    """Test path validation with auto construction."""
    p = ConfigPath(TEST_PATH)
    p.validate()
    captured = capsys.readouterr()
    assert captured.out == \
        "The path '/tmp/test/foo' is required by your configuration.\n"
