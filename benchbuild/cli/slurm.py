#!/usr/bin/env python3
"""
Dump SLURM script that executes the selected experiment with all projects.

This basically provides the same as benchbuild run, except that it just
dumps a slurm batch script that executes everything as an array job
on a configurable SLURM cluster.
"""
import os
import sys

from plumbum import cli

from benchbuild import experiment, plugins, project
from benchbuild.cli.main import BenchBuild
from benchbuild.settings import CFG
from benchbuild.utils import slurm


@BenchBuild.subcommand("slurm")
class Slurm(cli.Application):
    """ Generate a SLURM script. """

    def __init__(self, executable):
        super().__init__(executable)
        self._experiment = None
        self._group_names = None
        self._description = None

    @cli.switch(["-E", "--experiment"],
                str,
                mandatory=True,
                help="Specify experiments to run")
    def experiment(self, cfg_experiment):
        """Specify experiments to run"""
        self._experiment = cfg_experiment

    @cli.switch(["-D", "--description"],
                str,
                help="A description for this experiment run")
    def experiment_tag(self, description):
        """A description for this experiment run"""
        self._description = description

    @cli.switch(["-G", "--group"],
                str,
                list=True,
                requires=["--experiment"],
                help="Run a group of projects under the given experiments")
    def group(self, groups):
        """Run a group of projects under the given experiments"""
        self._group_names = groups

    subcommand = cli.SwitchAttr(['-S', '--subcommand'],
                                str,
                                requires=['--experiment'],
                                default='run',
                                help='Provide a subcommand for benchbuild.')

    def main(self, *projects: str) -> None:
        """Main entry point of benchbuild run."""
        cli_experiment = [self._experiment]
        group_names = self._group_names

        plugins.discover()

        discovered_experiments = experiment.discovered()

        if self._description:
            CFG["experiment_description"] = self._description

        CFG["slurm"]["logs"] = os.path.abspath(
            os.path.join(str(CFG['build_dir']), str(CFG['slurm']['logs']))
        )

        CFG["build_dir"] = str(CFG["slurm"]["node_dir"])

        wanted_experiments = {
            name: cls
            for name, cls in discovered_experiments.items()
            if name in set(cli_experiment)
        }
        unknown_experiments = [
            name for name in cli_experiment
            if name not in set(discovered_experiments.keys())
        ]

        if unknown_experiments:
            print(
                'Could not find ', str(unknown_experiments),
                ' in the experiment registry.'
            )
            sys.exit(1)

        prjs = project.populate(list(projects), group_names)
        for exp_cls in wanted_experiments.values():
            exp = exp_cls(projects=list(prjs.values()))
            print("Experiment: ", exp.name)
            slurm.script(exp, self.subcommand)
