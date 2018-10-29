"""
postgresql experiment within gentoo chroot.
"""
from time import sleep

from plumbum import local
from psutil import Process

from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils import wrapping
from benchbuild.utils.cmd import kill, su


class Postgresql(GentooGroup):
    """
    dev-db/postgresql
    """
    NAME = "postgresql"
    DOMAIN = "dev-db/postgresql"

    def compile(self):
        self.emerge_env = dict(USE="server")
        super(Postgresql, self).compile()

        pg_socketdir = local.path("/run/postgresql")
        if not pg_socketdir.exists():
            pg_socketdir.mkdir()

    def run_tests(self, runner):
        pg_data = local.path("/test-data/")
        pg_path = local.path("/usr/bin/postgres")

        postgres = wrapping.wrap(pg_path, self)

        def pg_su(command):
            return su['-c', command, '-g', 'postgres', 'postgres']

        dropdb = pg_su('/usr/bin/dropdb')
        createdb = pg_su("/usr/bin/createdb")
        pgbench = pg_su("/usr/bin/pgbench")
        initdb = pg_su("/usr/bin/initdb")
        pg_server = pg_su(pg_path)

        with local.env(PGPORT="54329", PGDATA=pg_data):
            if not pg_data.exists():
                runner(initdb)

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
                real_postgres = [
                    c.pid for c in postgres_root.children(True)
                    if c.name() == 'postgres.bin'
                    and c.parent().name() != 'postgres.bin'
                ]
                try:
                    runner(createdb)
                    runner(pgbench["-i", "portage"])
                    runner(pgbench["-c", 1, "-S", "-t", 1000000, "portage"])
                    runner(dropdb["portage"])
                finally:
                    kill("-sSIGTERM", real_postgres[0])
