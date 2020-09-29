#!/usr/bin/env python3

from benchbuild.cli.bootstrap import BenchBuildBootstrap
from benchbuild.cli.config import BBConfig
from benchbuild.cli.experiment import BBExperiment
from benchbuild.cli.log import BenchBuildLog
from benchbuild.cli.main import BenchBuild
from benchbuild.cli.project import BBProject
from benchbuild.cli.run import BenchBuildRun
from benchbuild.cli.slurm import Slurm
from benchbuild.environments.entrypoints import cli


def main(*args):
    """Main function."""

    BenchBuild.subcommand('bootstrap', BenchBuildBootstrap)
    BenchBuild.subcommand('config', BBConfig)
    BenchBuild.subcommand('container', cli.BenchBuildContainer)
    BenchBuild.subcommand('experiment', BBExperiment)
    BenchBuild.subcommand('log', BenchBuildLog)
    BenchBuild.subcommand('project', BBProject)
    BenchBuild.subcommand('run', BenchBuildRun)
    BenchBuild.subcommand('slurm', Slurm)

    return BenchBuild.run(*args)
