from os import getenv

from benchbuild.project import Project
from benchbuild.environments import container
from benchbuild.source import Git
from benchbuild.utils.cmd import make


class LevelDB(Project):
    NAME: str = 'leveldb'
    DOMAIN: str = 'database'
    GROUP: str = 'benchbuild'
    SOURCE = [
        Git(remote='https://github.com/google/leveldb',
            local='leveldb.src',
            limit=5,
            refspec='HEAD')
    ]
    CONTAINER = container.Buildah().from_('debian:buster-slim')

    def compile(self):
        leveldb_repo = local.path(self.source_of('leveldb.src'))

        clang = compiler.cc(self)
        clang_cxx = compiler.cxx(self)

        with local.cwd(leveldb_repo):
            with local.env(CXX=str(clang_cxx), CC=str(clang)):
                make_ = run.watch(make)
                make_("clean")
                make_("all", "-i")

    def run_tests(self):
        """
        Execute LevelDB's runtime configuration.

        Args:
            experiment: The experiment's run function.
        """
        leveldb_repo = local.path(self.source_of('leveldb.src'))

        leveldb = wrapping.wrap(leveldb_repo / "out-static" / "db_bench", self)
        leveldb = run.watch(leveldb)
        with local.env(LD_LIBRARY_PATH="{}:{}".format(
                leveldb_repo / "out-shared", getenv("LD_LIBRARY_PATH", ""))):
            leveldb()
