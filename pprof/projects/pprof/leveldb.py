#!/usr/bin/evn python
#

from pprof.project import ProjectFactory
from pprof.projects.pprof.group import PprofGroup
from os import path
from plumbum import FG, local


class LevelDB(PprofGroup):
    NAME = 'leveldb'
    DOMAIN = 'database'

    src_uri = "https://github.com/google/leveldb"

    class Factory:
        def create(self, exp):
            return LevelDB(exp, "leveldb", "database")

    ProjectFactory.addFactory("LevelDB", Factory())

    def download(self):
        from pprof.utils.downloader import Git

        with local.cwd(self.builddir):
            Git(self.src_uri, "leveldb.src")

    def configure(self):
        pass

    def build(self):
        from plumbum.cmd import make
        from pprof.utils.compiler import lt_clang, lt_clang_cxx
        from pprof.utils.run import run

        leveldb_dir = path.join(self.builddir, "leveldb.src")

        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags,
                             self.compiler_extension)
            clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                     self.compiler_extension)

        with local.cwd(leveldb_dir):
            with local.env(CXX=str(clang_cxx), CC=str(clang)):
                run(make["clean", "db_bench"])

    def run_tests(self, experiment):
        from pprof.project import wrap
        from pprof.utils.run import run
        """execute leveldb's db_bench script

        :experiment: the experiment's runner function

        """
        leveldb_dir = path.join(self.builddir, "leveldb.src")
        exp = wrap(path.join(leveldb_dir, "db_bench"), experiment)
        run(exp)
