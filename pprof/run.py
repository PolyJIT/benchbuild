#!/usr/bin/env python3
from plumbum import cli
from plumbum.cmd import mkdir
from pprof.driver import PollyProfiling
from pprof.settings import config
from pprof.utils.user_interface import query_yes_no
from pprof.experiments import *

import os, os.path


@PollyProfiling.subcommand("run")
class PprofRun(cli.Application):
    """ Frontend for running experiments in the pprof study framework. """

    _experiment_names = []
    _project_names = []
    _list = False
    _list_experiments = False
    _group_name = None

    @cli.switch(["-T", "--testdir"], str, help="Where are the testinput files")
    def testdir(self, dirname):
        config["testdir"] = dirname

    @cli.switch(["-S", "--sourcedir"], str, help="Where are the source files")
    def sourcedir(self, dirname):
        config["sourcedir"] = dirname

    @cli.switch(["--llvm-srcdir"], str, help="Where are the llvm source files")
    def llvm_sourcedir(self, dirname):
        config["llvm-srcdir"] = dirname

    @cli.switch(["-B", "--builddir"], str, help="Where should we build")
    def builddir(self, dirname):
        config["builddir"] = dirname

    @cli.switch(["--likwid-prefix"], str, help="Where is likwid installed?")
    def likwiddir(self, dirname):
        config["likwiddir"] = dirname

    @cli.switch(["-L", "--llvmdir"], str, help="Where is llvm?")
    def llvmdir(self, dirname):
        config["llvmdir"] = dirname

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
        config["experiment_description"] = description

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
        config["keep"] = True

    @cli.switch(["-G", "--group"],
                str,
                requires=["--experiment"],
                help="Run a group of projects under the given experiments")
    def group(self, group):
        self._group_name = group

    def main(self):
        from pprof.experiment import ExperimentRegistry

        if self._list_experiments:
            for exp_name in ExperimentRegistry.experiments:
                exp_cls = ExperimentRegistry.experiments[exp_name]
                print(exp_cls.NAME)
                docstring = exp_cls.__doc__ or "-- no docstring --"
                print(("    " + docstring))
            exit(0)

        if self._list:
            for exp_name in self._experiment_names:
                exp_cls = ExperimentRegistry.experiments[exp_name]
                exp = exp_cls(self._project_names, self._group_name)
                print_projects(exp)
            exit(0)

        if (self.show_config):
            from pprof.settings import print_settings
            print_settings(config)
            exit(0)

        if self._project_names:
            # Only try to create the build dir if we're actually running some projects.
            builddir = os.path.abspath(config["builddir"])
            if not os.path.exists(builddir):
                response = query_yes_no(
                    "The build directory {dirname} does not exist yet. Create it?".format(
                        dirname=builddir),
                    "no")
                if response:
                    mkdir("-p", builddir)

        for exp_name in self._experiment_names:
            print("Running experiment: " + exp_name)
            name = exp_name.lower()

            if exp_name in ExperimentRegistry.experiments:
                exp_cls = ExperimentRegistry.experiments[exp_name]
                exp = exp_cls(project_names, group_name)
                exp.clean()
                exp.prepare()
                exp.run()
            else:
                from logging import error
                error("Could not find {} in the experiment registry.",
                      exp_name)


def print_projects(experiment):
    """Print a list of projects registered for that experiment.

    :experiment: TODO

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
