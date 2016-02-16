"""
postgresql experiment within gentoo chroot.
"""
from os import path
from pprof.projects.gentoo.gentoo import GentooGroup
from pprof.utils.run import run, uchroot
from plumbum import local
from plumbum.cmd import tar  # pylint: disable=E0401


class Postgresql(GentooGroup):
    """
    dev-db/postgresql
    """
    NAME = "gentoo-postgresql"
    DOMAIN = "dev-db/postgresql"

    def build(self):
        with local.cwd(self.builddir):
            emerge_in_chroot = uchroot()["/usr/bin/emerge"]
            with local.env(USE="server"):
                run(emerge_in_chroot["dev-db/postgresql:9.4"])

    def run_tests(self, experiment):
        from pprof.project import wrap
        import asyncio

        pg_ctl = uchroot()["/usr/bin/pg_ctl"]
        dropdb = uchroot()["/usr/bin/dropdb"]
        createdb = uchroot()["/usr/bin/createdb"]
        pgbench = uchroot()["/usr/bin/pgbench"]
        initdb = uchroot()["/usr/bin/initdb"]

        initdb("-D", "/test-data")
        pg_path = path.join(self.builddir, "usr", "lib64", "postgresql-9.4",
                            "bin", "postgres")
        wrap(pg_path, experiment, self.builddir)
        postgres = uchroot()[pg_path]

        @asyncio.coroutine
        def start_postgres():
            run(postgres["-D", "/test-data"])

        num_clients = 1
        num_transactions = 1000000
        loop = asyncio.get_event_loop()
        pg_start = asyncio.async(start_postgres)
        try:
            dropdb("pgbench", recode=None)
            createdb("pgbench")
            pgbench("-i", "pgbench")
            pgbench("-c", num_clients, "-S", "-t", num_transactions, "pgbench")
            dropdb("pgbench")
        finally:
            pg_ctl("stop", "-t", 360, "-w", "-D", "/test-data", retcode=None)

        loop.run_until_complete(asyncio.wait(pg_start))
