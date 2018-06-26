#!/usr/bin/env python3

from benchbuild.cli import *
from benchbuild.cli.main import BenchBuild


def main(*args):
    """Main function."""
    return BenchBuild.run(*args)
