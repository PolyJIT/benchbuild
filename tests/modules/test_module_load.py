import importlib
import pytest
import sys
import benchbuild.module as mods

@pytest.fixture
def modules():
    yield {'bzip2': 'https://gitlab.lairosiel.de/benchbuild/bzip2.git'}

def test_module_discovery(modules):
    loaded = mods.create_modules(modules)
    assert len(loaded) == len(modules)

def test_init_environment(modules):
    discovered = mods.create_modules(modules)
    loaded = mods.init_environment(discovered)
    assert len(loaded) == len(modules)
    for m in loaded:
        assert m.__class__ == importlib.types.ModuleType