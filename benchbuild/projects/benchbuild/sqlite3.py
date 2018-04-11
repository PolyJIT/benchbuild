from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import make, unzip
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.downloader import Git, Wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


class SQLite3(Project):
    """ SQLite3 """

    NAME = 'sqlite3'
    DOMAIN = 'database'
    GROUP = 'benchbuild'

    src_dir = "sqlite-amalgamation-3080900"
    SRC_FILE = src_dir + ".zip"

    src_uri = "http://www.sqlite.org/2015/" + SRC_FILE

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        unzip(self.SRC_FILE)
        type(self).fetch_leveldb()

    def configure(self):
        pass

    def build(self):
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)

        with local.cwd(self.src_dir):
            run(clang["-fPIC", "-I.", "-c", "sqlite3.c"])
            run(clang["-shared", "-o", "libsqlite3.so", "sqlite3.o", "-ldl"])

        self.build_leveldb()

    @staticmethod
    def fetch_leveldb():
        src_uri = "https://github.com/google/leveldb"
        Git(src_uri, "leveldb.src")

    def build_leveldb(self):
        sqlite_dir = self.src_dir
        leveldb_dir = "leveldb.src"

        # We need to place sqlite3 in front of all other flags.
        self.ldflags += ["-L{0}".format(path.abspath(sqlite_dir))]
        self.cflags += ["-I{0}".format(path.abspath(sqlite_dir))]
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)

        with local.cwd(leveldb_dir):
            with local.env(CXX=str(clang_cxx), CC=str(clang)):
                run(make["clean", "out-static/db_bench_sqlite3"])

    def run_tests(self, experiment, runner):
        leveldb_dir = "leveldb.src"
        with local.cwd(leveldb_dir):
            with local.env(LD_LIBRARY_PATH=path.abspath(self.src_dir)):
                sqlite = wrap(path.join("out-static", "db_bench_sqlite3"),
                              experiment)
                run(sqlite)
