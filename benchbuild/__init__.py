# pylint: disable=useless-import-alias
"""
Public API of benchbuild.
"""
import sys

# Project utilities
from benchbuild.project import populate as populate

# Export: Source Code handling
from . import plugins as __PLUGINS__
from . import source as source
from .experiment import Experiment as Experiment
# Export: Project
from .project import Project as Project
# Export: Configuration
from .settings import CFG as CFG
# Don't Export, just init.
# Export: compiler, download, run and wrapping modules
from .utils import compiler as compiler
from .utils import download as download
from .utils import settings as __SETTINGS__
from .utils import wrapping as wrapping
# Wrapping / Execution utilities
from .utils.run import watch as watch
from .utils.wrapping import wrap as wrap


def __init__() -> None:
    """Initialize all plugins and settings."""
    if __PLUGINS__.discover():
        __SETTINGS__.setup_config(CFG)


__init__()

# Clean the namespace
del sys
del __PLUGINS__
del __SETTINGS__
