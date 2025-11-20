"""
Test path creation functions from benchbuild's settings module.
"""
import os
import pathlib
import unittest

import pytest
import yaml

from benchbuild.utils.settings import (ConfigPath, path_constructor,
                                       path_representer)


def test_root_path():
    """Test root path construction."""
    # Root path should be the OS-specific root separator
    assert str(ConfigPath([])) == os.path.sep


def test_simple_path():
    """Test simple path construction."""
    # Should create an absolute path with 'tmp' as a component
    expected = os.path.sep + 'tmp'
    assert str(ConfigPath(['tmp'])) == expected


def test_nested_path():
    """Test nested path construction."""
    # Use a platform-specific test path
    test_path = os.path.join('tmp', 'test', 'foo')
    expected = os.path.sep + test_path
    assert str(ConfigPath(test_path)) == expected


def test_construct():
    """Test path construction from YAML."""
    # Use platform-specific path for testing
    test_path = os.path.join('tmp', 'test', 'foo')
    test_path_obj = f"{{'test': !create-if-needed '{os.path.sep}{test_path}'}}"
    expected_config_path = {'test': ConfigPath(test_path)}
    
    yaml.add_constructor("!create-if-needed",
                         path_constructor,
                         Loader=yaml.SafeLoader)

    assert yaml.safe_load(test_path_obj) == expected_config_path


def test_represent():
    """Test scalar representation."""
    # Use platform-specific path for testing
    test_path = os.path.join('tmp', 'test', 'foo')
    config_path = {'test': ConfigPath(test_path)}
    expected_yaml = f"test: !create-if-needed '{os.path.sep}{test_path}'\n"
    
    yaml.add_representer(ConfigPath, path_representer, Dumper=yaml.SafeDumper)
    assert yaml.safe_dump(config_path) == expected_yaml


def test_path_validation(capsys, tmp_path, monkeypatch):
    """Test path validation with auto construction."""
    
    # Create a path that doesn't exist
    if os.name == 'nt':
        # Apply the mock
        # On Windows, use a simple relative path 
        test_path = os.path.join("test_dir", "nonexistent")
    else:
        # On Unix, use absolute path
        test_path = str(tmp_path / "nonexistent")
    
    p = ConfigPath(test_path)
    p.validate()
    captured = capsys.readouterr()
    
    # Should print the path requirement message
    assert "is required by your configuration." in captured.out
