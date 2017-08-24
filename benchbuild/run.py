#!/usr/bin/env python3
"""
benchbuild's run command.

This subcommand executes experiments on a set of user-controlled projects.
See the output of benchbuild run --help for more information.
"""
import logging
import os
import sys
import time
from plumbum import cli
from benchbuild.settings import CFG
from benchbuild.utils.actions import Step, Experiment, StepResult
from benchbuild.utils import progress, user_interface as ui
from benchbuild import experiments
from benchbuild import experiment


LOG = logging.getLogger(__name__)


class BenchBuildRun(cli.Application):
    """Frontend for running experiments in the benchbuild study framework."""

    _experiment_names = []
    _project_names = []
    _list = False
    _list_experiments = False
    _group_name = None
    _test_full = False

    @cli.switch(["--full"], help="Test all experiments for the project")
    def full(self):
        self._test_full = True

    @cli.switch(["-E", "--experiment"],
                str,
                list=True,
                help="Specify experiments to run")
    def experiments(self, experiments):
        self._experiment_names = experiments

    @cli.switch(["-D", "--description"],
                str,
                help="A description for this experiment run")
    def experiment_tag(self, description):
        CFG["experiment_description"] = description

    @cli.switch(["-P", "--project"],
                str,
                list=True,
                help="Specify projects to run")
    def projects(self, projects):
        self._project_names = projects

    @cli.switch(["-L", "--list-experiments"],
                help="List available experiments")
    def list_experiments(self):
        self._list_experiments = True

    @cli.switch(["-l", "--list"],
                requires=["--experiment"],
                help="List available projects for experiment")
    def list_projects(self):
        self._list = True

    show_config = cli.Flag(["-d", "--dump-config"],
                           help="Just dump benchbuild's config and exit.",
                           default=False)

    store_config = cli.Flag(["-s", "--save-config"],
                            help="Save benchbuild's configuration.",
                            default=False)

    @cli.switch(["-G", "--group"],
                str,
                requires=["--experiment"],
                help="Run a group of projects under the given experiments")
    def group(self, group):
        self._group_name = group

    pretend = cli.Flag(['p', 'pretend'], default=False)

    def main(self):
        """Main entry point of benchbuild run."""
        from benchbuild.utils.cmd import mkdir  # pylint: disable=E0401

        project_names = self._project_names
        group_name = self._group_name

        experiments.discover()

        registry = experiment.ExperimentRegistry
        exps = registry.experiments

        if self._list_experiments:
            for exp_name in registry.experiments:
                exp_cls = exps[exp_name]
                print(exp_cls.NAME)
                docstring = exp_cls.__doc__ or "-- no docstring --"
                print(("    " + docstring))
            exit(0)

        if self._list:
            for exp_name in self._experiment_names:
                exp_cls = exps[exp_name]
                exp = exp_cls(self._project_names, self._group_name)
                print_projects(exp)
            exit(0)

        if self.show_config:
            print(repr(CFG))
            exit(0)

        if self.store_config:
            config_path = ".benchbuild.yml"
            CFG.store(config_path)
            print("Storing config in {0}".format(os.path.abspath(config_path)))
            exit(0)

        if self._project_names:
            builddir = os.path.abspath(str(CFG["build_dir"]))
            if not os.path.exists(builddir):
                response = True
                if sys.stdin.isatty():
                    response = ui.query_yes_no(
                        "The build directory {dirname} does not exist yet."
                        "Should I create it?".format(dirname=builddir),
                        "no")

                if response:
                    mkdir("-p", builddir)
                    print("Created directory {0}.".format(builddir))

        actns = []

        exps_to_run = []
        if self._test_full:
            exps_to_run = exps.values()
        else:
            if len(self._experiment_names) == 0:
                print("No experiment selected. Did you forget to use -E?")
            for exp_name in self._experiment_names:
                if exp_name in exps:
                    exps_to_run.append(exps[exp_name])
                else:
                    LOG.error("Could not find %s in the experiment registry.",
                              exp_name)

        for exp_cls in exps_to_run:
            exp = exp_cls(project_names, group_name)
            eactn = Experiment(exp, exp.actions())
            actns.append(eactn)

        num_actions = sum([len(x) for x in actns])
        print("Number of actions to execute: {}".format(num_actions))
        for a in actns:
            print(a)
        print()

        failed = []
        start = 0
        end = 0
        if self.pretend:
            return 0

        def has_failed(res):
            fstatus = [StepResult.ERROR, StepResult.CAN_CONTINUE]
            return len([x for x in res if x in fstatus]) > 0

        pg_bar = progress.ProgressBar(
            width=80,
            pg_char='|',
            length=num_actions,
            has_output=CFG["verbosity"].value() > 0,
            body=True,
            timer=False)

        def on_step_end(step, f):
            pg_bar.increment()

        Step.ON_STEP_END.append(on_step_end)

        pg_bar.start()
        start = time.perf_counter()
        for action in actns:
            res = action()

            if has_failed(res):
                failed.append(action)

        end = time.perf_counter()
        pg_bar.done()

        print("""
Summary:
    {num_total} actions were in the queue.
    {num_failed} actions failed to execute.

    This run took: {elapsed_time:8.3f} seconds.
        """.format(num_total=num_actions, num_failed=len(failed),
                   elapsed_time=end-start))

        if failed:
            print("Failed:")
            for fail in failed:
                print(fail)

        return len(failed)


def print_projects(exp):
    """
    Print a list of projects registered for that experiment.

    Args:
        exp: The experiment to print all projects for.

    """
    grouped_by = {}
    projects = exp.projects
    for name in projects:
        prj = projects[name]

        if prj.GROUP not in grouped_by:
            grouped_by[prj.GROUP] = []

        grouped_by[prj.GROUP].append(name)

    for name in grouped_by:
        from textwrap import wrap
        print(">> {0}".format(name))
        projects = sorted(grouped_by[name])
        project_paragraph = ""
        for prj in projects:
            project_paragraph += ", {0}".format(prj)
        print("\n".join(wrap(project_paragraph[2:],
                             80,
                             break_on_hyphens=False,
                             break_long_words=False)))
        print()
