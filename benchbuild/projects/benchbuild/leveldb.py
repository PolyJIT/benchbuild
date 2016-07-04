from benchbuild.project import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.downloader import Git
from benchbuild.utils.run import run

from plumbum import local
from benchbuild.utils.cmd import make

from os import path


class LevelDB(BenchBuildGroup):
    NAME = 'leveldb'
    DOMAIN = 'database'

    src_uri = "https://github.com/google/leveldb"
    src_dir = "leveldb.src"

    def download(self):
        Git(self.src_uri, self.src_dir)

    def configure(self):
        pass

    def build(self):
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)

        with local.cwd(self.src_dir):
            with local.env(CXX=str(clang_cxx), CC=str(clang)):
                run(make["clean", "out-static/db_bench"])

    def run_tests(self, experiment):
        """
        Execute LevelDB's runtime configuration.

        Args:
            experiment: The experiment's run function.
        """
        exp = wrap(
            path.join(self.src_dir, "out-static", "db_bench"), experiment)
        run(exp)
