#!/usr/bin/env python3
"""
benchbuild's run command.

This subcommand executes experiments on a set of user-controlled projects.
See the output of benchbuild run --help for more information.
"""
import logging
import os
import time

from plumbum import cli

import benchbuild.experiment as experiment
import benchbuild.experiments as experiments
import benchbuild.project as project
import benchbuild.utils.actions as actions
from benchbuild.settings import CFG
from benchbuild.utils import path, progress

LOG = logging.getLogger(__name__)


class BenchBuildRun(cli.Application):
    """Frontend for running experiments in the benchbuild study framework."""

    experiment_names = []
    project_names = []
    group_name = None

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

    @cli.switch(
        ["-P", "--project"], str, list=True, help="Specify projects to run")
    def set_projects(self, names):
        self.project_names = names

    list_experiments = cli.Flag(
        ["-L", "--list-experiments"],
        help="List available experiments",
        default=False)

    list_projects = cli.Flag(
        ["-l", "--list"],
        requires=["--experiment"],
        help="List available projects for experiment",
        default=False)

    show_progress = cli.Flag(
        ["--disable-progress"], help="Disable progress bar", default=True)

    show_config = cli.Flag(
        ["-d", "--dump-config"],
        help="Just dump benchbuild's config and exit.",
        default=False)

    store_config = cli.Flag(
        ["-s", "--save-config"],
        help="Save benchbuild's configuration.",
        default=False)

    @cli.switch(
        ["-G", "--group"],
        str,
        requires=["--experiment"],
        help="Run a group of projects under the given experiments")
    def set_group(self, group):
        self.group_name = group

    pretend = cli.Flag(['p', 'pretend'], default=False)

    def __maybe_list_experiments(self, exps):
        if not self.list_experiments:
            return

        for exp_cls in exps.values():
            print(exp_cls.NAME)
            docstring = exp_cls.__doc__ or "-- no docstring --"
            print(("    " + docstring))
        exit(0)

    def __maybe_list_projects(self, exps, prjs):
        if not self.list_projects:
            return

        for exp_cls in exps.values():
            exp = exp_cls(projects=prjs)
            print_projects(exp)
        exit(0)

    def __maybe_show_config(self, cfg):
        if not self.show_config:
            return

        print(repr(cfg))
        exit(0)

    def __maybe_store_config(self, cfg):
        if not self.store_config:
            config_path = ".benchbuild.yml"
            cfg.store(config_path)
            print("Storing config in {0}".format(os.path.abspath(config_path)))
            exit(0)

    def __generate_plan(self, exps, prjs, cfg):
        if prjs:
            path.mkdir_interactive(cfg["build_dir"].value())

        for exp_cls in exps.values():
            exp = exp_cls(projects=prjs)
            eactn = actions.Experiment(obj=exp, actions=exp.actions())
            yield eactn

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
            has_output=cfg["verbosity"].value() > 0,
            body=True,
            timer=False)

        def on_step_end(step, func):
            del step, func
            pg_bar.increment()

        actions.Step.ON_STEP_END.append(on_step_end)
        return pg_bar

    def main(self):
        """Main entry point of benchbuild run."""
        experiment_names = self.experiment_names
        project_names = self.project_names
        group_name = self.group_name

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
        prjs = project.populate(project_names, group_name)

        self.__maybe_list_experiments(all_exps)
        self.__maybe_list_projects(exps, prjs)
        self.__maybe_show_config(CFG)

        if not experiment_names:
            print("No experiment selected. Did you forget to use -E?")

        plan = list(self.__generate_plan(exps, prjs, CFG))
        num_actions = actions.num_steps(plan)
        actions.print_steps(plan)

        if self.pretend:
            exit(0)

        if self.show_progress:
            pg_bar = type(self).setup_progress(CFG, num_actions)
            pg_bar.start()

        start = time.perf_counter()
        failed = execute_plan(plan)
        end = time.perf_counter()

        if self.show_progress:
            pg_bar.done()

        print_summary(num_actions, failed, end - start)
        return len(failed)


def execute_plan(plan):
    """"Execute the plan.

    Args:
        plan (:obj:`list` of :obj:`actions.Step`): The plan we want to execute.

    Returns:
        (:obj:`list` of :obj:`actions.Step`): A list of failed actions.
    """
    results = [action() for action in plan]
    return [result for result in results if actions.step_has_failed(result)]


def print_projects(exp):
    """
    Print a list of projects registered for that experiment.

    Args:
        exp: The experiment to print all projects for.

    """
    grouped_by = {}
    projects = exp.projects
    if not projects:
        print(
            "Your selection didn't include any projects for this experiment.")

    for name in projects:
        prj = projects[name]

        if prj.GROUP not in grouped_by:
            grouped_by[prj.GROUP] = []

        grouped_by[prj.GROUP].append(prj.NAME)

    for name in grouped_by:
        from textwrap import wrap
        print(">> {0}".format(name))
        projects = sorted(grouped_by[name])
        project_paragraph = ""
        for prj in projects:
            project_paragraph += ", {0}".format(prj)
        print("\n".join(
            wrap(
                project_paragraph[2:],
                80,
                break_on_hyphens=False,
                break_long_words=False)))
        print()


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

    if failed:
        print("Failed:")
        for fail in failed:
            print(fail)
