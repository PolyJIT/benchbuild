#!/usr/bin/env python
# encoding: utf-8

from plumbum import cli
from pprof import PollyProfiling
from settings import config

import experiments.polli
import experiments.polyjit
import experiments.raw
import logging
import pprint
log = logging.getLogger()


@PollyProfiling.subcommand("run")
class PprofRun(cli.Application):

    """ Frontend for running experiments in the pprof study framework """

    _experiments = {"polyjit": experiments.polyjit.PolyJIT,
                    "polli": experiments.polli.Polli,
                    "raw": experiments.raw.RawRuntime}

    _experiment_names = []
    _project_names = []
    _verbose = False
    _clean = False
    _list = False
    _execute = False
    _collect = False

    @cli.switch(["-T", "--testdir"], str, help="Where are the testinput files")
    def testdir(self, dirname):
        config["testdir"] = dirname

    @cli.switch(["-S", "--sourcedir"], str, help="Where are the source files")
    def sourcedir(self, dirname):
        config["sourcedir"] = dirname

    @cli.switch(["-B", "--builddir"], str, help="Where should we build")
    def builddir(self, dirname):
        config["builddir"] = dirname

    @cli.switch(["--likwid-prefix"], str, help="Where is likwid installed?")
    def likwiddir(self, dirname):
        config["likwiddir"] = dirname

    @cli.switch(["-L", "--llvmdir"], str, help="Where is llvm?")
    def llvmdir(self, dirname):
        config["llvmdir"] = dirname

    @cli.switch(
        ["-E", "--experiment"], str, list=True,
        help="Specify experiments to run")
    def experiments(self, experiments):
        self._experiment_names = experiments

    @cli.switch(
        ["-P", "--project"], str, list=True, help="Specify projects to run")
    def projects(self, projects):
        self._project_names = projects

    @cli.switch(["-c", "--clean"], help="Clean products")
    def clean(self):
        self._clean = True

    @cli.switch(["-x", "--execute"], help="Execute experiments")
    def execute(self):
        self._execute = True

    @cli.switch(["-C", "--collect"], help="Collect results")
    def collect(self):
        self._collect = True

    @cli.switch(["-l", "--list"], requires=["--experiment"],
                help="List available projects for experiment")
    def list(self):
        self._list = True

    def main(self):
        if self._list:
            for exp in self._experiment_names:
                experiment = self._experiments[exp](exp, self._project_names)
                print "\n".join(experiment.projects)
            exit(0)

        for exp_name in self._experiment_names:
            log.info("Running experiment: " + exp_name)
            name = exp_name.lower()

            exp = self._experiments[name](name, self._project_names)

            if self._clean:
                exp.clean()

            if self._execute:
                log.info("Configuration: ")
                pprint.pprint(config)
                exp.prepare()
                exp.run()

            if self._collect:
                exp.collect_results()
