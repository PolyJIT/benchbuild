"""
postgresql experiment within gentoo chroot.
"""
from os import path
from pprof.projects.gentoo.gentoo import GentooGroup
from pprof.utils.run import run, uchroot
from plumbum import local, BG, FG
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
        from threading import Condition, Thread

        num_clients = 1
        num_transactions = 1000000
        pg_path = path.join(self.builddir, "usr", "lib64", "postgresql-9.4",
                            "bin", "postgres")
        pg_data = "/test-data/"

        wrap(pg_path, experiment, self.builddir)
        cuchroot = uchroot(uid=250, gid=250)

        pg_ctl = cuchroot["/usr/bin/pg_ctl"]
        dropdb = cuchroot["/usr/bin/dropdb"]
        createdb = cuchroot["/usr/bin/createdb"]
        pgbench = cuchroot["/usr/bin/pgbench"]
        initdb = cuchroot["/usr/bin/initdb"]
        mkdir = cuchroot["/bin/mkdir"]
        pg_server = cuchroot["/usr/lib64/postgresql-9.4/bin/postgres"]
        bash = cuchroot["/bin/bash"]

        pg_socketdir_base = "/run/postgresql"
        pg_socketdir = path.join(self.builddir, pg_socketdir_base)
        if not path.exists(pg_socketdir):
            mkdir("-p", pg_socketdir)

        pg_up = Condition()
        test_ready = Condition()

        with local.env(PGPORT="54329",
                       PGDATA=pg_data):
            def run_postgres():
                with local.env(PGPORT="54329",
                               PGDATA=pg_data):
                    pg_server & BG
                with pg_up:
                    bash & FG
                    pg_up.notify()
                with test_ready:
                    test_ready.wait()

            bg_postgres = Thread(target=run_postgres)
            try:
                initdb()
                with pg_up:
                    bg_postgres.start()
                    pg_up.wait()
                createdb()
                # By default, portage should have uid/gid=250 in a stage3 tarball
                pgbench("-i", "portage")
                pgbench("-c", num_clients, "-S", "-t", num_transactions, "portage")
                dropdb("portage")
            finally:
                pg_ctl("stop", "-t", 360, "-w", retcode=None)
                with test_ready:
                    test_ready.notify()
                bg_postgres.join()
