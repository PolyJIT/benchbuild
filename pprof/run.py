#!/usr/bin/env python
# encoding: utf-8

from plumbum import cli
from pprof.driver import PollyProfiling
from pprof.settings import config

from pprof.experiments import polli
from pprof.experiments import polyjit
from pprof.experiments import raw
from pprof.experiments import papi
import logging
import pprint
log = logging.getLogger()


@PollyProfiling.subcommand("run")
class PprofRun(cli.Application):

    """ Frontend for running experiments in the pprof study framework """

    _experiments = {"polyjit": polyjit.PolyJIT,
                    "polli": polli.Polli,
                    "polli-baseline": polli.PolliBaseLine,
                    "raw": raw.RawRuntime,
                    "papi": papi.PapiScopCoverage
                    }

    _experiment_names = []
    _project_names = []
    _verbose = False
    _clean = False
    _list = False
    _execute = False
    _collect = False
    _group_name = None

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

    @cli.switch(["-G", "--group"], str, requires=["--experiment"], help="Run a group of projects under the given experiments")
    def group(self, group):
        self._group_name = group

    def main(self):
        if self._list:
            for exp in self._experiment_names:
                experiment = self._experiments[exp](
                    exp, self._project_names, self._group_name)
                print_projects(experiment)
            exit(0)

        for exp_name in self._experiment_names:
            log.info("Running experiment: " + exp_name)
            name = exp_name.lower()

            exp = self._experiments[name](
                name, self._project_names, self._group_name)
            synchronize_experiment_with_db(exp)

            if self._clean:
                exp.clean()

            if self._execute:
                log.info("Configuration: ")
                pprint.pprint(config)
                exp.prepare()
                exp.run()

            if self._collect:
                exp.collect_results()


def print_projects(experiment):
    """Print a list of projects registered for that experiment

    :experiment: TODO

    """
    grouped_by = {}
    projects = experiment.projects
    for name in projects:
        p = projects[name]

        if not p.group_name in grouped_by:
            grouped_by[p.group_name] = []

        grouped_by[p.group_name].append(name)

    for name in grouped_by:
        from textwrap import wrap
        print ">> {}".format(name)
        projects = sorted(grouped_by[name])
        project_paragraph = ""
        for p in projects:
            project_paragraph += ", {}".format(p)
        print "\n".join(wrap(project_paragraph[2:], 80, break_on_hyphens=False,
                             break_long_words=False))
        print


def synchronize_experiment_with_db(exp):
    """Synchronize information about the given experiment with the pprof
    database

    :exp: The experiment we want to synchronize

    """
    from pprof.utils import db
    conn = db.get_db_connection()

    sql_sel = "SELECT * FROM experiment WHERE name=%s"
    sql_ins = "INSERT INTO experiment (name, description) VALUES (%s, %s)"
    sql_upd = "UPDATE experiment SET description = %s WHERE name = %s"
    with conn.cursor() as c:
        c.execute(sql_sel, (exp.name, ))

        if not c.rowcount:
            c.execute(sql_ins, (exp.name, exp.name))
        else:
            c.execute(sql_upd, [exp.name, exp.name])
    conn.commit()
