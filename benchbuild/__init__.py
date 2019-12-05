"""
Public API of benchbuild.
"""
import sys
from typing import Callable, Optional
from plumbum.commands import BaseCommand
from plumbum import local, Path

from . import experiments as __EXPERIMENTS__
from . import projects as __PROJECTS__
from . import reports as __REPORTS__
from .downloads.base import BaseSource
from .project import Project
from .settings import CFG
from .utils import compiler, download, run
from .utils import settings as __SETTINGS__
from .utils import wrapping

__EXPERIMENTS__.discover()
__PROJECTS__.discover()
__REPORTS__.discover()
__SETTINGS__.setup_config(CFG)

cwd = local.cwd
env = local.env
path = local.path

wrap = wrapping.wrap
watch = run.watch

del local
del sys
del BaseCommand
del BaseSource
del Path
del __EXPERIMENTS__
del __PROJECTS__
del __REPORTS__
del __SETTINGS__
