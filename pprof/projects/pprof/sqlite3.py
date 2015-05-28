#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local


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
        from pprof.utils.compiler import clang

        sqlite_dir = path.join(self.builddir, self.src_dir)

        with local.cwd(sqlite_dir):
            clang()(self.cflags, "-fPIC", "-c", "sqlite3.c")
            clang()("-shared", "-Wl,-soname,libsqlite3.so.0", "-o",
                    "libsqlite3.so",
                    "sqlite3.o", self.ldflags + ["-ldl"])
        self.build_leveldb()

    def fetch_leveldb(self):
        src_uri = "https://github.com/google/leveldb"

        with local.cwd(self.builddir):
            from pprof.utils.downloader import Git
            Git(src_uri, "leveldb.src")

    def build_leveldb(self):
        from plumbum.cmd import make, ln

        llvm = path.join(config["llvmdir"], "bin")
        clang_cxx = local[path.join(llvm, "clang++")]
        clang = local[path.join(llvm, "clang")]

        leveldb_dir = path.join(self.builddir, "leveldb.src")
        sqlite_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(leveldb_dir):
            with local.env(CXX=str(clang_cxx),
                           CC=str(clang),
                           CFLAGS=" ".join(self.cflags),
                           CXXFLAGS=" ".join(self.cflags),
                           LDFLAGS=" ".join(self.ldflags + ["-L", sqlite_dir]),
                           ):
                make["clean", "db_bench_sqlite3"] & FG

        with local.cwd(self.builddir):
            ln("-sf", path.join(leveldb_dir, "db_bench_sqlite3"), self.run_f)
