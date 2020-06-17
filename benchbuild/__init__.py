"""
Public API of benchbuild.
"""
import sys

from plumbum import local

# Project utilities
from benchbuild.project import populate

# Export: Source Code handling
from . import experiments as __EXPERIMENTS__
from . import projects as __PROJECTS__
from . import reports as __REPORTS__
from . import source
# Export: Project
from .project import Project
# Export: Configuration
from .settings import CFG
# Export: compiler, download, run and wrapping modules
from .utils import compiler, download, run
from .utils import settings as __SETTINGS__
from .utils import wrapping


def __init__() -> None:
    """Initialize all plugins and settings."""
    __EXPERIMENTS__.discover()
    __PROJECTS__.discover()
    __REPORTS__.discover()
    __SETTINGS__.setup_config(CFG)


__init__()

# Forwards to plumbum
cwd = local.cwd
env = local.env
path = local.path

# Wrapping / Execution utilities
wrap = wrapping.wrap
watch = run.watch

# Clean the namespace
del local
del sys
del __EXPERIMENTS__
del __PROJECTS__
del __REPORTS__
del __SETTINGS__
