#!/usr/bin/env python
# encoding: utf-8


from plumbum import cli
from plumbum.cmd import mkdir
from pprof.driver import PollyProfiling
from pprof.settings import config
from pprof.utils.user_interface import query_yes_no

import os, os.path
import pprint


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

    @cli.switch(["-E", "--experiment"], str, list=True,
                help="Specify experiments to run")
    def experiments(self, experiments):
        self._experiment_names = experiments

    @cli.switch(["-D", "--description"], str,
                help="A description for this experiment run")
    def experiment_tag(self, description):
        config["experiment_description"] = description

    @cli.switch(
        ["-P", "--project"], str, list=True, requires=["--experiment"],
        help="Specify projects to run")
    def projects(self, projects):
        self._project_names = projects

    @cli.switch(["--list-experiments"],
                help="List available experiments")
    def list_experiments(self):
        self._list_experiments = True

    @cli.switch(["-l", "--list"], requires=["--experiment"],
                help="List available projects for experiment")
    def list(self):
        self._list = True

    @cli.switch(["-k", "--keep"], requires=["--experiment"],
                help="Keep intermediate results")
    def keep(self):
        config["keep"] = True

    @cli.switch(["-G", "--group"], str, requires=["--experiment"],
                help="Run a group of projects under the given experiments")
    def group(self, group):
        self._group_name = group

    def main(self):
        from pprof.experiments import polyjit
        from pprof.experiments import raw
        from pprof.experiments import papi
        from pprof.experiments.polly import (polly, openmp, openmpvect,
                                             vectorize)
        from pprof.experiments import compilestats, compilestats_ewpt

        self._experiments = {
            "pj-raw": polyjit.PJITRaw,
            "pj-perf": polyjit.PJITperf,
            "pj-likwid": polyjit.PJITlikwid,
            "pj-cs": polyjit.PJITcs,
            "pj-papi": polyjit.PJITpapi,
            "raw": raw.RawRuntime,
            "papi": papi.PapiScopCoverage,
            "papi-std": papi.PapiStandardScopCoverage,
            "polly": polly.Polly,
            "polly-openmp": openmp.PollyOpenMP,
            "polly-openmpvect": openmpvect.PollyOpenMPVectorizer,
            "polly-vectorize": vectorize.PollyVectorizer,
            "stats": compilestats.CompilestatsExperiment,
            "ewpt": compilestats_ewpt.EWPTCompilestatsExperiment,
        }

        if self._list_experiments:
            for experiment_name, experiment in self._experiments.items():
                print(experiment_name)
                docstring = experiment.__doc__ or "-- no docstring --"
                docstring = docstring.strip()
                print("    " + docstring)
            exit(0)

        if self._list:
            for exp in self._experiment_names:
                experiment = self._experiments[exp](
                    exp, self._project_names, self._group_name)
                print_projects(experiment)
            exit(0)

        print "Configuration: "
        pprint.pprint(config)

        if self._project_names:
            # Only try to create the build dir if we're actually running some projects.
            builddir = os.path.abspath(config["builddir"])
            if not os.path.exists(builddir):
                response = query_yes_no("The build directory {dirname} does not exist yet. Create it?".format(dirname=builddir), "no")
                if response:
                    mkdir("-p", builddir)

        for exp_name in self._experiment_names:
            print "Running experiment: " + exp_name
            name = exp_name.lower()

            exp = self._experiments[name](
                name, self._project_names, self._group_name)
            exp.clean()
            exp.prepare()
            exp.run()


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
        print ">> {}".format(name)
        projects = sorted(grouped_by[name])
        project_paragraph = ""
        for prj in projects:
            project_paragraph += ", {}".format(prj)
        print "\n".join(wrap(project_paragraph[2:], 80, break_on_hyphens=False,
                             break_long_words=False))
        print
