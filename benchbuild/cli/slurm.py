#!/usr/bin/env python3
"""
Dump SLURM script that executes the selected experiment with all projects.

This basically provides the same as benchbuild run, except that it just
dumps a slurm batch script that executes everything as an array job
on a configurable SLURM cluster.
"""
import itertools
import os
import typing as tp

from plumbum import cli

from benchbuild import experiment, plugins, project
from benchbuild.cli.main import BenchBuild
from benchbuild.experiment import ExperimentIndex
from benchbuild.project import ProjectIndex
from benchbuild.settings import CFG
from benchbuild.utils import slurm


@BenchBuild.subcommand("slurm")
class Slurm(cli.Application):
    """ Generate a SLURM script. """

    group_args: tp.List[str] = []

    def __init__(self, executable):
        super().__init__(executable)
        self._experiment: str = ''
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
    def group(self, groups: tp.List[str]) -> None:  # type: ignore
        """Run a group of projects under the given experiments"""
        self.group_args = groups

    def main(self, *args: str) -> int:
        """Main entry point of benchbuild run."""
        plugins.discover()

        cli_experiments: tp.List[str] = [self._experiment]
        cli_groups = self.group_args
        cli_projects, cli_subcommand = split_args(args)

        wanted_experiments, wanted_projects = cli_process(
            cli_experiments, cli_projects, cli_groups
        )

        if self._description:
            CFG["experiment_description"] = self._description

        CFG["slurm"]["logs"] = os.path.abspath(
            os.path.join(str(CFG['build_dir']), str(CFG['slurm']['logs']))
        )

        CFG["build_dir"] = str(CFG["slurm"]["node_dir"])
        if CFG["slurm"]["container_root"].value is not None:
            CFG["container"]["root"] = CFG["slurm"]["container_root"].value
        if CFG["slurm"]["container_runroot"].value is not None:
            CFG["container"]["runroot"] = CFG["slurm"]["container_runroot"
                                                      ].value

        if not wanted_experiments:
            print("Could not find any experiment. Exiting.")
            return -1

        if not wanted_projects:
            print("No projects selected.")
            return -1

        for exp_cls in wanted_experiments.values():
            exp = exp_cls(projects=list(wanted_projects.values()))
            print("Experiment: ", exp.name)
            slurm.script(exp, *cli_subcommand)
        return 0


def split_args(
    args: tp.Iterable[str]
) -> tp.Tuple[tp.Iterable[str], tp.Iterable[str]]:
    """
    Split our CLI arguments at the '--' into two groups.

    The first group will be our projects. The second (optional) group
    will be a custom slurm command to use as subcommand to benchbuild.
    """
    subcommands: tp.Set[str] = {'run', 'container'}
    prj_or_slurm = list(args)
    cli_projects = list(
        itertools.takewhile(lambda x: x not in subcommands, prj_or_slurm)
    )
    cli_slurm_command = list(
        itertools.dropwhile(lambda x: x not in subcommands, prj_or_slurm)
    )
    if not cli_slurm_command:
        cli_slurm_command = ['run']

    return (cli_projects, cli_slurm_command)


def cli_process(
    cli_experiments: tp.Iterable[str], cli_projects: tp.Iterable[str],
    cli_groups: tp.Iterable[str]
) -> tp.Tuple[ExperimentIndex, ProjectIndex]:
    """
    Shared CLI processing of projects/experiment selection.
    """
    discovered_experiments = experiment.discovered()
    wanted_experiments = {
        name: cls
        for name, cls in discovered_experiments.items()
        if name in set(cli_experiments)
    }
    unknown_experiments = [
        name for name in cli_experiments
        if name not in set(discovered_experiments.keys())
    ]
    if unknown_experiments:
        print(
            'Could not find ', str(unknown_experiments),
            ' in the experiment registry.'
        )

    wanted_projects = project.populate(list(cli_projects), list(cli_groups))

    return (wanted_experiments, wanted_projects)
