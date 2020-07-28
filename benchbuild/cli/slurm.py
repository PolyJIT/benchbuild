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
        super(Slurm, self).__init__(executable)
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

    def main(self, *projects: str) -> None:
        """Main entry point of benchbuild run."""
        exp = [self._experiment]
        group_names = self._group_names

        plugins.discover()

        all_exps = experiment.discovered()

        if self._description:
            CFG["experiment_description"] = self._description

        CFG["slurm"]["logs"] = os.path.abspath(
            os.path.join(str(CFG['build_dir']), str(CFG['slurm']['logs'])))

        CFG["build_dir"] = str(CFG["slurm"]["node_dir"])

        exps = dict(filter(lambda pair: pair[0] in set(exp), all_exps.items()))
        unknown_exps = list(
            filter(lambda name: name not in all_exps.keys(), set(exp)))
        if unknown_exps:
            print('Could not find ', str(unknown_exps),
                  ' in the experiment registry.')
            sys.exit(1)

        prjs = project.populate(list(projects), group_names)
        for exp_cls in exps.values():
            exp = exp_cls(projects=prjs)
            print("Experiment: ", exp.name)
            CFG["slurm"]["node_dir"] = os.path.abspath(
                os.path.join(str(CFG["slurm"]["node_dir"]), str(exp.id)))
            slurm.script(exp)
