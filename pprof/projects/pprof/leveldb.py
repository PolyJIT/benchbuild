#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log
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
        from pprof.utils.compiler import lt_clang, lt_clang_cxx

        leveldb_dir = path.join(self.builddir, "leveldb.src")

        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags)
            clang_cxx = lt_clang_cxx(self.cflags, self.ldflags)

        with local.cwd(leveldb_dir):
            with local.env(CXX=str(clang_cxx),
                    CC=str(clang)):
                make["clean", "db_bench"] & FG

    def run_tests(self, experiment):
        from pprof.project import wrap

        """execute leveldb's db_bench script

        :experiment: the experiment's runner function

        """
        leveldb_dir = path.join(self.builddir, "leveldb.src")
        exp = wrap(path.join(leveldb_dir, "db_bench"), experiment)
        exp()
