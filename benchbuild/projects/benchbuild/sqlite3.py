from benchbuild.project import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.downloader import Wget, Git
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.run import run

from plumbum import local
from plumbum.cmd import unzip, make

from os import path


class SQLite3(BenchBuildGroup):
    """ SQLite3 """

    NAME = 'sqlite3'
    DOMAIN = 'database'

    src_dir = "sqlite-amalgamation-3080900"
    src_file = src_dir + ".zip"
    src_uri = "http://www.sqlite.org/2015/" + src_file

    def download(self):
        Wget(self.src_uri, self.src_file)
        unzip(self.src_file)
        self.fetch_leveldb()

    def configure(self):
        pass

    def build(self):
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)

        with local.cwd(self.src_dir):
            run(clang["-fPIC", "-I.", "-c", "sqlite3.c"])
            run(clang["-shared", "-Wl,-soname,libsqlite3.so.0", "-o",
                      "libsqlite3.so", "sqlite3.o", "-ldl"])

        self.build_leveldb()

    def fetch_leveldb(self):
        src_uri = "https://github.com/google/leveldb"
        Git(src_uri, "leveldb.src")

    def build_leveldb(self):
        sqlite_dir = self.src_dir
        leveldb_dir = "leveldb.src"

        # We need to place sqlite3 in front of all other flags.
        self.ldflags = ["-L", sqlite_dir] + self.ldflags
        self.cflags = ["-I", sqlite_dir] + self.cflags
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags)
        clang = lt_clang(self.cflags, self.ldflags)

        with local.cwd(leveldb_dir):
            with local.env(CXX=str(clang_cxx), CC=str(clang)):
                run(make["clean", "out-static/db_bench_sqlite3"])

    def run_tests(self, experiment):
        leveldb_dir = "leveldb.src"
        with local.cwd(leveldb_dir):
            sqlite = wrap(
                path.join(leveldb_dir, "out-static", "db_bench_sqlite3"),
                experiment)
            run(sqlite)
