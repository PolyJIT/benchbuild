"""
Setup plugins.
"""
from . import experiments as __EXPERIMENTS__
from . import projects as __PROJECTS__
from . import reports as __REPORTS__
from .settings import CFG as __CFG__
from .utils import settings as __SETTINGS__

__EXPERIMENTS__.discover()
__PROJECTS__.discover()
__REPORTS__.discover()
__SETTINGS__.setup_config(__CFG__)
