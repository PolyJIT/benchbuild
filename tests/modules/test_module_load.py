import pytest
import benchbuild.module as mods
from benchbuild.settings import CFG

@pytest.fixture
def modules():
    yield {'bzip2': 'https://gitlab.lairosiel.de/benchbuild/bzip2.git'}

def test_module_discovery(modules):
    loaded = mods.create_modules(modules)
    assert len(loaded) == 1
