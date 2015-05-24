#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local


class LevelDB(PprofGroup):

    class Factory:

        def create(self, exp):
            return LevelDB(exp, "leveldb", "database")
    ProjectFactory.addFactory("LevelDB", Factory())

    def download(self):
        src_uri = "https://github.com/google/leveldb"

        from pprof.utils.downloader import Git
        from plumbum.cmd import git

        with local.cwd(self.builddir):
            Git(src_uri, "leveldb.src")

    def configure(self):
        pass

    def build(self):
        from plumbum.cmd import make, ln

        llvm = path.join(config["llvmdir"], "bin")
        clang_cxx = local[path.join(llvm, "clang++")]
        clang = local[path.join(llvm, "clang")]
        leveldb_dir = path.join(self.builddir, "leveldb.src")

        with local.cwd(leveldb_dir):
            with local.env(CXX=str(clang_cxx),
                           CC=str(clang),
                           CFLAGS=" ".join(self.cflags),
                           CXXFLAGS=" ".join(self.cflags),
                           LDFLAGS=" ".join(self.ldflags)):
                make["clean", "db_bench"] & FG

        with local.cwd(self.builddir):
            dbg_ln = ln["-sf", path.join(leveldb_dir, "db_bench"), self.run_f]
            print dbg_ln
            dbg_ln & FG
