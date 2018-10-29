from os import getenv

from plumbum import local

from benchbuild import project
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import make


@download.with_git("https://github.com/google/leveldb", limit=5)
class LevelDB(project.Project):
    NAME = 'leveldb'
    DOMAIN = 'database'
    GROUP = 'benchbuild'
    SRC_FILE = 'leveldb.src'
    VERSION = 'HEAD'

    def compile(self):
        self.download()

        clang = compiler.cc(self)
        clang_cxx = compiler.cxx(self)
        with local.cwd(self.src_file):
            with local.env(CXX=str(clang_cxx), CC=str(clang)):
                make("clean")
                run.run(make["all", "-i"])

    def run_tests(self, runner):
        """
        Execute LevelDB's runtime configuration.

        Args:
            experiment: The experiment's run function.
        """
        leveldb = wrapping.wrap(
            local.path(self.src_file) / "out-static" / "db_bench", self)
        with local.env(LD_LIBRARY_PATH="{}:{}".format(
                local.path(self.src_file) /
                "out-shared", getenv("LD_LIBRARY_PATH", ""))):
            runner(leveldb)
