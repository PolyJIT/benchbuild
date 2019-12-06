from os import getenv

from plumbum import local

import benchbuild as bb

from benchbuild.downloads import Git
from benchbuild.utils.cmd import make


class LevelDB(bb.Project):
    NAME: str = 'leveldb'
    DOMAIN: str = 'database'
    GROUP: str = 'benchbuild'
    SOURCE = [
        Git(remote='https://github.com/google/leveldb',
            local='leveldb.src',
            limit=5,
            refspec='HEAD')
    ]

    def compile(self):
        leveldb_repo = bb.path(self.source_of('leveldb.src'))

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)

        with bb.cwd(leveldb_repo):
            with bb.env(CXX=str(clang_cxx), CC=str(clang)):
                make_ = bb.watch(make)
                make_("clean")
                make_("all", "-i")

    def run_tests(self):
        """
        Execute LevelDB's runtime configuration.

        Args:
            experiment: The experiment's run function.
        """
        leveldb_repo = bb.path(self.source_of('leveldb.src'))

        leveldb = bb.wrap(leveldb_repo / "out-static" / "db_bench", self)
        leveldb = bb.watch(leveldb)
        with bb.env(LD_LIBRARY_PATH="{}:{}".format(
                leveldb_repo / "out-shared", getenv("LD_LIBRARY_PATH", ""))):
            leveldb()
