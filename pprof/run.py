#!/usr/bin/env python3
"""
pprof's run command.

This subcommand executes experiments on a set of user-controlled projects.
See the output of pprof run --help for more information.
"""
import os
from plumbum import cli
from plumbum.cmd import mkdir  # pylint: disable=E0401
from pprof.driver import PollyProfiling
from pprof.settings import CFG
from pprof.utils.user_interface import query_yes_no
from pprof import experiments  # pylint: disable=W0611
from pprof import experiment


@PollyProfiling.subcommand("run")
class PprofRun(cli.Application):
    """Frontend for running experiments in the pprof study framework."""

    _experiment_names = []
    _project_names = []
    _list = False
    _list_experiments = False
    _group_name = None

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
                requires=["--experiment"],
                help="Specify projects to run")
    def projects(self, projects):
        self._project_names = projects

    @cli.switch(["--list-experiments"], help="List available experiments")
    def list_experiments(self):
        self._list_experiments = True

    @cli.switch(["-l", "--list"],
                requires=["--experiment"],
                help="List available projects for experiment")
    def list(self):
        self._list = True

    show_config = cli.Flag(["-d", "--dump-config"],
                           help="Just dump pprof's config and exit.",
                           default=False)

    @cli.switch(["-k", "--keep"],
                requires=["--experiment"],
                help="Keep intermediate results")
    def keep(self):
        CFG["keep"] = True

    @cli.switch(["-G", "--group"],
                str,
                requires=["--experiment"],
                help="Run a group of projects under the given experiments")
    def group(self, group):
        self._group_name = group

    def main(self):
        """Main entry point of pprof run."""
        from logging import getLogger, INFO
        project_names = self._project_names
        group_name = self._group_name
        registry = experiment.ExperimentRegistry
        exps = registry.experiments
        root = getLogger()
        root.setLevel(INFO)

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

        if (self.show_config):
            print(repr(CFG))
            exit(0)

        if self._project_names:
            builddir = os.path.abspath(str(CFG["build_dir"]))
            if not os.path.exists(builddir):
                response = query_yes_no(
                    "The build directory {dirname} does not exist yet."
                    "Should I create it?".format(dirname=builddir), "no")
                if response:
                    mkdir("-p", builddir)

        for exp_name in self._experiment_names:
            print("Running experiment: " + exp_name)
            if exp_name in exps:
                exp_cls = exps[exp_name]
                exp = exp_cls(project_names, group_name)
                exp.clean()
                exp.prepare()
                exp.run()
            else:
                from logging import error
                error("Could not find {} in the experiment registry.",
                      exp_name)


def print_projects(experiment):
    """
    Print a list of projects registered for that experiment.

    Args:
        experiment: The experiment to print all projects for.

    """
    grouped_by = {}
    projects = experiment.projects
    for name in projects:
        prj = projects[name]

        if prj.group_name not in grouped_by:
            grouped_by[prj.group_name] = []

        grouped_by[prj.group_name].append(name)

    for name in grouped_by:
        from textwrap import wrap
        print(">> {}".format(name))
        projects = sorted(grouped_by[name])
        project_paragraph = ""
        for prj in projects:
            project_paragraph += ", {}".format(prj)
        print("\n".join(wrap(project_paragraph[2:],
                             80,
                             break_on_hyphens=False,
                             break_long_words=False)))
        print()
