from benchbuild.utils.wrapping import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.downloader import Git
from benchbuild.utils.run import run
from benchbuild.utils.versions import get_version_from_cache_dir

from plumbum import local
from benchbuild.utils.cmd import make

from os import path, getenv


class LevelDB(BenchBuildGroup):
    NAME = 'leveldb'
    DOMAIN = 'database'
    SRC_FILE = 'leveldb.src'
    VERSION = get_version_from_cache_dir(SRC_FILE)

    src_uri = "https://github.com/google/leveldb"

    def download(self):
        Git(self.src_uri, self.SRC_FILE)

    def configure(self):
        pass

    def build(self):
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)

        with local.cwd(self.SRC_FILE):
            with local.env(CXX=str(clang_cxx), CC=str(clang)):
                make("clean")
                run(make["all", "-i"])

    def run_tests(self, experiment):
        """
        Execute LevelDB's runtime configuration.

        Args:
            experiment: The experiment's run function.
        """
        exp = wrap(
            path.join(self.SRC_FILE, "out-shared", "db_bench"), experiment)
        with local.env(LD_LIBRARY_PATH="{}:{}".format(
                path.join(self.SRC_FILE, "out-shared"),
                getenv("LD_LIBRARY_PATH", ""))):
            run(exp)
