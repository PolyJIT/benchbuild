#!/usr/bin/env python3
"""
benchbuild's run command.

This subcommand executes experiments on a set of user-controlled projects.
See the output of benchbuild run --help for more information.
"""
import logging
import sys
import time
import typing as tp

from plumbum import cli

from benchbuild import engine, experiment, plugins, project
from benchbuild.settings import CFG

LOG = logging.getLogger(__name__)


class BenchBuildRun(cli.Application):
    """Frontend for running experiments in the benchbuild study framework."""

    experiment_names: tp.List[str] = []
    group_names = None

    test_full = cli.Flag(["-F", "--full"],
                         help="Test all experiments for the project",
                         default=False)

    @cli.switch(["-E", "--experiment"],
                str,
                list=True,
                help="Specify experiments to run")
    def set_experiments(self, names):
        self.experiment_names = names

    @cli.switch(["-D", "--description"],
                str,
                help="A description for this experiment run")
    def set_experiment_tag(self, description):
        CFG["experiment_description"] = description

    @cli.switch(["-G", "--group"],
                str,
                list=True,
                requires=["--experiment"],
                help="Run a group of projects under the given experiments")
    def set_group(self, groups):
        self.group_names = groups

    pretend = cli.Flag(['p', 'pretend'], default=False)

    def main(self, *projects: str) -> int:
        """Main entry point of benchbuild run."""
        experiment_names = self.experiment_names
        group_names = self.group_names

        plugins.discover()
        all_exps = experiment.discovered()

        if self.test_full:
            exps = all_exps
        else:
            exps = dict(
                filter(
                    lambda pair: pair[0] in set(experiment_names),
                    all_exps.items()
                )
            )

        unknown_exps = list(
            filter(
                lambda name: name not in all_exps.keys(), set(experiment_names)
            )
        )
        if unknown_exps:
            print(
                'Could not find ', str(unknown_exps),
                ' in the experiment registry.'
            )
        prjs = project.populate(list(projects), group_names)
        if not prjs:
            print("Could not find any project. Exiting.")
            return 1

        if not exps:
            print("Could not find any experiment. Exiting.")
            return -2

        ngn = engine.Experimentator(
            experiments=list(exps.values()), projects=list(prjs.values())
        )
        num_actions = ngn.num_actions
        ngn.print_plan()

        if self.pretend:
            sys.exit(0)

        start = time.perf_counter()
        failed = ngn.start()
        end = time.perf_counter()

        print_summary(num_actions, failed, end - start)
        return len(failed)


def print_summary(num_actions, failed, duration):
    """
    Print a small summary of the executed plan.

    Args:
        num_actions (int): Total size of the executed plan.
        failed (:obj:`list` of :obj:`actions.Step`): List of failed actions.
        duration: Time we spent executing the plan.
    """
    num_failed = len(failed)
    print(
        """
Summary:
{num_total} actions were in the queue.
{num_failed} actions failed to execute.

This run took: {elapsed_time:8.3f} seconds.
    """.format(
            num_total=num_actions, num_failed=num_failed, elapsed_time=duration
        )
    )
