from os import getenv

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import make
from benchbuild.utils.compiler import cc, cxx
from benchbuild.utils.downloader import with_git
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


@with_git("https://github.com/google/leveldb", limit=5)
class LevelDB(Project):
    NAME = 'leveldb'
    DOMAIN = 'database'
    GROUP = 'benchbuild'
    SRC_FILE = 'leveldb.src'
    VERSION = 'HEAD'

    def compile(self):
        self.download()

        clang = cc(self)
        clang_cxx = cxx(self)
        with local.cwd(self.src_file):
            with local.env(CXX=str(clang_cxx), CC=str(clang)):
                make("clean")
                run(make["all", "-i"])

    def run_tests(self, runner):
        """
        Execute LevelDB's runtime configuration.

        Args:
            experiment: The experiment's run function.
        """
        exp = wrap(local.path(self.src_file) / "out-static" / "db_bench", self)
        with local.env(LD_LIBRARY_PATH="{}:{}".format(
                local.path(self.src_file) /
                "out-shared", getenv("LD_LIBRARY_PATH", ""))):
            runner(exp)
