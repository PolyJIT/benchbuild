"""
postgresql experiment within gentoo chroot.
"""
from os import path
from time import sleep
from psutil import Process
from benchbuild.utils.wrapping import wrap_in_uchroot as wrap
from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils.run import uretry, uchroot
from plumbum import local
from benchbuild.utils.cmd import kill, mkdir  # pylint: disable=E0401


run = uretry


class Postgresql(GentooGroup):
    """
    dev-db/postgresql
    """
    NAME = "gentoo-postgresql"
    DOMAIN = "dev-db/postgresql"

    def build(self):
        emerge_in_chroot = uchroot()["/usr/bin/emerge"]
        with local.env(USE="server"):
            run(emerge_in_chroot["dev-db/postgresql:9.4"])

        pg_socketdir = "/run/postgresql"
        if not path.exists(self.outside(pg_socketdir)):
            run(mkdir["-p", self.outside(pg_socketdir)])

    def outside(self, chroot_path):
        """
        Return the path with the outside prefix.

        Args:
            chroot_path: the path inside the chroot.

        Returns:
            Absolute path outside this chroot.
        """

        return path.join(self.builddir, chroot_path.lstrip("/"))

    def run_tests(self, experiment, run):
        pg_data = "/test-data/"
        pg_path = "/usr/lib64/postgresql-9.4/bin/postgres"
        wrap(self.outside(pg_path), experiment, self.builddir)
        cuchroot = uchroot(uid=250, gid=250)

        dropdb = cuchroot["/usr/bin/dropdb"]
        createdb = cuchroot["/usr/bin/createdb"]
        pgbench = cuchroot["/usr/bin/pgbench"]
        initdb = cuchroot["/usr/bin/initdb"]
        pg_server = cuchroot[pg_path]

        with local.env(PGPORT="54329", PGDATA=pg_data):
            if not path.exists(self.outside(pg_data)):
                run(initdb)

            with pg_server.bgrun() as postgres:
                #We get the PID of the running 'pg_server, which is actually
                #the PID of the uchroot binary. This is not the PID we
                #want to send a SIGTERM to.

                #We need to enumerate all children of 'postgres' recursively
                #and select the one PID that is named 'postgres.bin' and has
                #not a process with the same name as parent.
                #This should be robust enough, as long as postgres doesn't
                #switch process names after forking.
                sleep(3)
                postgres_root = Process(pid=postgres.pid)
                real_postgres = [c.pid
                                 for c in postgres_root.children(True)
                                 if c.name() == 'postgres.bin' and c.parent(
                                 ).name() != 'postgres.bin']
                try:
                    run(createdb)
                    run(pgbench["-i", "portage"])
                    run(pgbench["-c", 1, "-S", "-t", 1000000, "portage"])
                    run(dropdb["portage"])
                finally:
                    kill("-sSIGTERM", real_postgres[0])
