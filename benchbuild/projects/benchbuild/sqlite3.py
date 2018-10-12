from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import make, unzip
from benchbuild.utils.compiler import cc, cxx
from benchbuild.utils.downloader import Git, with_wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


@with_wget({
    '3080900':
    'http://www.sqlite.org/2015/sqlite-amalgamation-3080900.zip'
})
class SQLite3(Project):
    """ SQLite3 """

    NAME = 'sqlite3'
    DOMAIN = 'database'
    GROUP = 'benchbuild'
    VERSION = '3080900'
    SRC_FILE = 'sqlite.zip'

    def compile(self):
        self.download()
        unzip(self.src_file)
        unpack_dir = local.path('sqlite-amalgamation-{0}'.format(self.version))

        SQLite3.fetch_leveldb()

        clang = cc(self)

        with local.cwd(unpack_dir):
            run(clang["-fPIC", "-I.", "-c", "sqlite3.c"])
            run(clang["-shared", "-o", "libsqlite3.so", "sqlite3.o", "-ldl"])

        self.build_leveldb()

    @staticmethod
    def fetch_leveldb():
        src_uri = "https://github.com/google/leveldb"
        Git(src_uri, "leveldb.src")

    def build_leveldb(self):
        sqlite_dir = local.path('sqlite-amalgamation-{0}'.format(self.version))
        leveldb_dir = "leveldb.src"

        # We need to place sqlite3 in front of all other flags.
        self.ldflags += ["-L{0}".format(path.abspath(sqlite_dir))]
        self.cflags += ["-I{0}".format(path.abspath(sqlite_dir))]
        clang_cxx = cxx(self)
        clang = cc(self)

        with local.cwd(leveldb_dir):
            with local.env(CXX=str(clang_cxx), CC=str(clang)):
                run(make["clean", "out-static/db_bench_sqlite3"])

    def run_tests(self, runner):
        leveldb_dir = "leveldb.src"
        with local.cwd(leveldb_dir):
            with local.env(LD_LIBRARY_PATH=path.abspath(self.src_dir)):
                sqlite = wrap(
                    path.join("out-static", "db_bench_sqlite3"), self)
                run(sqlite)
