from os import getenv, path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import make
from benchbuild.utils.compiler import cc, cxx
from benchbuild.utils.downloader import Git
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


class LevelDB(Project):
    NAME = 'leveldb'
    DOMAIN = 'database'
    GROUP = 'benchbuild'
    SRC_FILE = 'leveldb.src'

    src_uri = "https://github.com/google/leveldb"

    def download(self):
        Git(self.src_uri, self.SRC_FILE)

    def configure(self):
        pass

    def build(self):
        clang = cc(self)
        clang_cxx = cxx(self)
        with local.cwd(self.SRC_FILE):
            with local.env(CXX=str(clang_cxx), CC=str(clang)):
                make("clean")
                run(make["all", "-i"])

    def run_tests(self, runner):
        """
        Execute LevelDB's runtime configuration.

        Args:
            experiment: The experiment's run function.
        """
        exp = wrap(
            path.join(self.SRC_FILE, "out-static", "db_bench"), self)
        with local.env(LD_LIBRARY_PATH="{}:{}".format(
                path.join(self.SRC_FILE, "out-shared"),
                getenv("LD_LIBRARY_PATH", ""))):
            runner(exp)
