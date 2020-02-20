"""The CLI package."""
__all__ = [
    "main", "bootstrap", "config", "container", "experiment", "log", "project",
    "report", "run", "slurm"
]

from . import *
from .main import BenchBuild


def __main__(*args):
    """Main function."""
    return BenchBuild.run(*args)