"""Test user interface utility methods."""
import os

import pytest

from benchbuild.utils.user_interface import ask


@pytest.fixture
def env():
    os.putenv("TEST", "yes")


def test_ask(env):
    assert ask("Test?", default_answer=True) == True
    assert ask("Test?", default_answer=False) == False
