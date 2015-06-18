#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory
from pprof.projects.pprof.group import PprofGroup

from os import path
from plumbum import local


class SQLite3(PprofGroup):

    """ SQLite3 """

    class Factory:

        def create(self, exp):
            return SQLite3(exp, "sqlite3", "database")
    ProjectFactory.addFactory("SQLite3", Factory())

    src_dir = "sqlite-amalgamation-3080900"
    src_file = src_dir + ".zip"
    src_uri = "http://www.sqlite.org/2015/" + src_file

    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import unzip

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            unzip(self.src_file)
            self.fetch_leveldb()

    def configure(self):
        pass

    def build(self):
        from pprof.utils.compiler import lt_clang

        with local.cwd(self.builddir):
            sqlite_dir = path.join(self.builddir, self.src_dir)
            clang = lt_clang(self.cflags, self.ldflags,
                             self.compiler_extension)

        with local.cwd(sqlite_dir):
            clang("-fPIC", "-I.", "-c", "sqlite3.c")
            clang("-shared", "-Wl,-soname,libsqlite3.so.0",
                  "-o", "libsqlite3.so", "sqlite3.o", "-ldl")

        with local.cwd(self.builddir):
            self.build_leveldb()

    def fetch_leveldb(self):
        src_uri = "https://github.com/google/leveldb"

        with local.cwd(self.builddir):
            from pprof.utils.downloader import Git
            Git(src_uri, "leveldb.src")

    def build_leveldb(self):
        from pprof.utils.compiler import lt_clang, lt_clang_cxx
        from plumbum.cmd import make

        sqlite_dir = path.join(self.builddir, self.src_dir)
        leveldb_dir = path.join(self.builddir, "leveldb.src")

        self.ldflags += ["-L", sqlite_dir]
        self.cflags += ["-I", sqlite_dir]
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags)
        clang = lt_clang(self.cflags, self.ldflags)

        with local.cwd(leveldb_dir):
            with local.env(CXX=str(clang_cxx),
                           CC=str(clang)):
                make("clean", "db_bench_sqlite3")

    def run_tests(self, experiment):
        from pprof.project import wrap

        leveldb_dir = path.join(self.builddir, "leveldb.src")
        with local.cwd(leveldb_dir):
            sqlite = wrap(
                path.join(leveldb_dir, "db_bench_sqlite3"), experiment)
            sqlite()
