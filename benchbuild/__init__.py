# pylint: disable=useless-import-alias
"""
Public API of benchbuild.
"""
import sys

import plumbum as pb

# Project utilities
from benchbuild.project import populate as populate

# Export: Source Code handling
from . import experiments as __EXPERIMENTS__
from . import projects as __PROJECTS__
from . import reports as __REPORTS__
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
    __EXPERIMENTS__.discover()
    __PROJECTS__.discover()
    __REPORTS__.discover()
    __SETTINGS__.setup_config(CFG)


__init__()

# Forwards to plumbum
cwd = pb.local.cwd
env = pb.local.env
path = pb.local.path

# Clean the namespace
del sys
del pb
del __EXPERIMENTS__
del __PROJECTS__
del __REPORTS__
del __SETTINGS__
