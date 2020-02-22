from benchbuild.environments import container
from benchbuild.project import Project
from benchbuild.source import Git, HTTP
from benchbuild.utils.cmd import make, unzip


class SQLite3(Project):
    """ SQLite3 """

    NAME: str = 'sqlite3'
    DOMAIN: str = 'database'
    GROUP: str = 'benchbuild'
    SOURCE = [
        HTTP(remote={
            '3080900':
            'http://www.sqlite.org/2015/sqlite-amalgamation-3080900.zip'
        },
             local='sqlite.zip'),
        Git(remote='https://github.com/google/leveldb',
            local='leveldb.src',
            refspec='HEAD',
            limit=5)
    ]
    CONTAINER = container.Buildah().from_('debian:buster-slim')

    def compile(self):
        sqlite_source = local.path(self.source_of('sqlite.zip'))
        sqlite_version = self.version_of('sqlite.zip')
        unzip(sqlite_source)
        unpack_dir = local.path(f'sqlite-amalgamation-{sqlite_version}')

        clang = compiler.cc(self)
        clang = run.watch(clang)

        with local.cwd(unpack_dir):
            clang("-fPIC", "-I.", "-c", "sqlite3.c")
            clang("-shared", "-o", "libsqlite3.so", "sqlite3.o", "-ldl")

        self.build_leveldb()

    def build_leveldb(self):
        sqlite_version = self.version_of('sqlite.zip')

        sqlite_dir = local.path(f'sqlite-amalgamation-{sqlite_version}')
        leveldb_repo = local.path(self.source_of('leveldb.src'))

        # We need to place sqlite3 in front of all other flags.
        self.ldflags += ["-L{0}".format(sqlite_dir)]
        self.cflags += ["-I{0}".format(sqlite_dir)]
        clang_cxx = compiler.cxx(self)
        clang = compiler.cc(self)

        with local.cwd(leveldb_repo):
            with local.env(CXX=str(clang_cxx), CC=str(clang)):
                make_ = run.watch(make)
                make_("clean", "out-static/db_bench_sqlite3")

    def run_tests(self):
        leveldb_repo = local.path(self.source_of('leveldb.src'))
        with local.cwd(leveldb_repo):
            with local.env(LD_LIBRARY_PATH=leveldb_repo):
                sqlite = wrapping.wrap(
                    leveldb_repo / 'out-static' / 'db_bench_sqlite3', self)
                sqlite = run.watch(sqlite)
                sqlite()
