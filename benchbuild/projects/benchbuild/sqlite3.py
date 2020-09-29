from plumbum import local

import benchbuild as bb
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.source import HTTP, Git
from benchbuild.utils.cmd import make, unzip


class SQLite3(bb.Project):
    """ SQLite3 """

    NAME = 'sqlite3'
    DOMAIN = 'database'
    GROUP = 'benchbuild'
    SOURCE = [
        HTTP(
            remote={
                '3080900':
                    'http://www.sqlite.org/2015/sqlite-amalgamation-3080900.zip'
            },
            local='sqlite.zip'
        ),
        Git(
            remote='https://github.com/google/leveldb',
            local='leveldb.src',
            refspec='HEAD',
            limit=5
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def compile(self):
        sqlite_source = local.path(self.source_of('sqlite.zip'))
        sqlite_version = self.version_of('sqlite.zip')
        unzip(sqlite_source)
        unpack_dir = local.path(f'sqlite-amalgamation-{sqlite_version}')

        clang = bb.compiler.cc(self)
        _clang = bb.watch(clang)

        with local.cwd(unpack_dir):
            _clang("-fPIC", "-I.", "-c", "sqlite3.c")
            _clang("-shared", "-o", "libsqlite3.so", "sqlite3.o", "-ldl")

        self.build_leveldb()

    def build_leveldb(self):
        sqlite_version = self.version_of('sqlite.zip')

        sqlite_dir = local.path(f'sqlite-amalgamation-{sqlite_version}')
        leveldb_repo = local.path(self.source_of('leveldb.src'))

        # We need to place sqlite3 in front of all other flags.
        self.ldflags += ["-L{0}".format(sqlite_dir)]
        self.cflags += ["-I{0}".format(sqlite_dir)]
        clang_cxx = bb.compiler.cxx(self)
        clang = bb.compiler.cc(self)

        with local.cwd(leveldb_repo):
            with local.env(CXX=str(clang_cxx), CC=str(clang)):
                _make = bb.watch(make)
                _make("clean", "out-static/db_bench_sqlite3")

    def run_tests(self):
        leveldb_repo = local.path(self.source_of('leveldb.src'))
        with local.cwd(leveldb_repo):
            with local.env(LD_LIBRARY_PATH=leveldb_repo):
                sqlite = bb.wrap(
                    leveldb_repo / 'out-static' / 'db_bench_sqlite3', self
                )
                _sqlite = bb.watch(sqlite)
                _sqlite()
