#!/usr/bin/env python3
"""
benchbuild's run command.

This subcommand executes experiments on a set of user-controlled projects.
See the output of benchbuild run --help for more information.
"""
import logging
import time

from plumbum import cli

from benchbuild import experiment, experiments, project
from benchbuild.cli.main import BenchBuild
from benchbuild.settings import CFG
from benchbuild.utils import actions, progress, tasks

LOG = logging.getLogger(__name__)


@BenchBuild.subcommand("run")
class BenchBuildRun(cli.Application):
    """Frontend for running experiments in the benchbuild study framework."""

    experiment_names = []
    group_names = None

    test_full = cli.Flag(
        ["-F", "--full"],
        help="Test all experiments for the project",
        default=False)

    @cli.switch(
        ["-E", "--experiment"],
        str,
        list=True,
        help="Specify experiments to run")
    def set_experiments(self, names):
        self.experiment_names = names

    @cli.switch(
        ["-D", "--description"],
        str,
        help="A description for this experiment run")
    def set_experiment_tag(self, description):
        CFG["experiment_description"] = description

    show_progress = cli.Flag(
        ["--disable-progress"], help="Disable progress bar", default=True)

    @cli.switch(
        ["-G", "--group"],
        str,
        list=True,
        requires=["--experiment"],
        help="Run a group of projects under the given experiments")
    def set_group(self, groups):
        self.group_names = groups

    pretend = cli.Flag(['p', 'pretend'], default=False)

    @staticmethod
    def setup_progress(cfg, num_actions):
        """Setup a progress bar.

        Args:
            cfg: Configuration dictionary.
            num_actions (int): Number of actions in the plan.

        Returns:
            The configured progress bar.
        """
        pg_bar = progress.ProgressBar(
            width=80,
            pg_char='|',
            length=num_actions,
            has_output=int(cfg["verbosity"]) > 0,
            body=True,
            timer=False)

        def on_step_end(step, func):
            del step, func
            pg_bar.increment()

        actions.Step.ON_STEP_END.append(on_step_end)
        return pg_bar

    def main(self, *projects):
        """Main entry point of benchbuild run."""
        experiment_names = self.experiment_names
        group_names = self.group_names

        experiments.discover()
        all_exps = experiment.ExperimentRegistry.experiments

        if self.test_full:
            exps = all_exps
        else:
            exps = dict(
                filter(lambda pair: pair[0] in set(experiment_names),
                       all_exps.items()))

        unknown_exps = list(
            filter(lambda name: name not in all_exps.keys(),
                   set(experiment_names)))
        if unknown_exps:
            print('Could not find ', str(unknown_exps),
                  ' in the experiment registry.')
        prjs = project.populate(projects, group_names)

        if not exps:
            print("Could not find any experiment. Exiting.")
            return -2

        plan = list(tasks.generate_plan(exps, prjs))
        num_actions = actions.num_steps(plan)
        actions.print_steps(plan)

        if self.pretend:
            exit(0)

        if self.show_progress:
            pg_bar = type(self).setup_progress(CFG, num_actions)
            pg_bar.start()

        start = time.perf_counter()
        failed = tasks.execute_plan(plan)
        end = time.perf_counter()

        if self.show_progress:
            pg_bar.done()

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
    print("""
Summary:
{num_total} actions were in the queue.
{num_failed} actions failed to execute.

This run took: {elapsed_time:8.3f} seconds.
    """.format(
        num_total=num_actions, num_failed=num_failed, elapsed_time=duration))
