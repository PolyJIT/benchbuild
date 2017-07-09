from benchbuild.projects.benchbuild.group import BenchBuildGroup

from plumbum import FG, local
from benchbuild.utils.cmd import cp, echo, chmod

from os import path


class Postgres(BenchBuildGroup):
    """ postgres benchmark """

    NAME = 'postgres'
    DOMAIN = 'database'

    testfiles = ["pg_ctl", "dropdb", "createdb", "pgbench"]

    def prepare(self):
        super(Postgres, self).prepare()

        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        for test_f in testfiles:
            cp("-a", test_f, self.builddir)

    def run_tests(self, experiment, run):
        exp = experiment(self.run_f)

        pg_ctl = local[path.join(self.builddir, "pg_ctl")]
        dropdb = local[path.join(self.builddir, "dropdb")]
        createdb = local[path.join(self.builddir, "createdb")]
        pgbench = local[path.join(self.builddir, "pgbench")]

        bin_name = path.join(self.builddir, self.name + ".sh")
        test_data = path.join(self.testdir, "test-data")

        (echo["#!/bin/sh"] >> bin_name)()
        (echo[str(exp)] >> bin_name)()
        chmod("+x", bin_name)

        num_clients = 1
        num_transactions = 1000000

        pg_ctl("stop", "-t", 360, "-w", "-D", test_data, retcode=None)
        try:
            with local.cwd(test_data):
                pg_ctl("start", "-p", bin_name, "-w", "-D", test_data)
            dropdb["pgbench"] & FG(retcode=None)
            createdb("pgbench")
            run(pgbench["-i", "pgbench"])
            run(pgbench[
                "-c", num_clients, "-S", "-t", num_transactions, "pgbench"])
            dropdb("pgbench")
            pg_ctl("stop", "-t", 360, "-w", "-D", test_data)
        except Exception:
            pg_ctl("stop", "-t", 360, "-w", "-D", test_data)
            raise
