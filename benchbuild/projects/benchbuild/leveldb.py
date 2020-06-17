from os import getenv

import benchbuild as bb
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import make


@download.with_git("https://github.com/google/leveldb", limit=5)
class LevelDB(bb.Project):
    NAME = 'leveldb'
    DOMAIN = 'database'
    GROUP = 'benchbuild'
    SRC_FILE = 'leveldb.src'
    VERSION = 'HEAD'

    def compile(self):
        self.download()

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)
        with bb.cwd(leveldb_repo):
            with bb.env(CXX=str(clang_cxx), CC=str(clang)):
                _make_ = bb.watch(make)
                _make("clean")
                _make("all", "-i")

    def run_tests(self):
        """
        Execute LevelDB's runtime configuration.

        Args:
            experiment: The experiment's run function.
        """
        leveldb = bb.wrap(
            bb.path(self.src_file) / "out-static" / "db_bench", self)
        _leveldb = bb.watch(leveldb)
        with bb.env(LD_LIBRARY_PATH="{}:{}".format(
                bb.path(self.src_file) /
                "out-shared", getenv("LD_LIBRARY_PATH", ""))):
            _leveldb()
