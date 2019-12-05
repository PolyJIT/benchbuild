from plumbum import local

from benchbuild import project
from benchbuild.downloads import Git
from benchbuild.utils import compiler, run, wrapping
from benchbuild.utils.cmd import git, make


class Minisat(project.Project):
    """ minisat benchmark """

    VERSION = 'HEAD'
    NAME: str = 'minisat'
    DOMAIN: str = 'verification'
    GROUP: str = 'benchbuild'
    SOURCE = [
        Git(remote='https://github.com/niklasso/minisat',
            local='minisat.git',
            limit=5,
            refspec='HEAD')
    ]

    def run_tests(self):
        minisat_repo = local.path(self.source[0].local)
        minisat_build = minisat_repo / 'build' / 'dynamic'
        minisat_lib = minisat_build / 'lib'
        minisat_bin = minisat_build / 'bin'
        testfiles = local.path(self.testdir) // "*.cnf.gz"

        minisat = wrapping.wrap(minisat_bin / "minisat", self)
        for test_f in testfiles:
            minisat_test = run.watch(
                (minisat.with_env(LD_LIBRARY_PATH=minisat_lib) < test_f))
            minisat_test()

    def compile(self):
        minisat_repo = local.path(self.source[0].local)
        with local.cwd(minisat_repo):
            # FIXME: That needs to be modeled with Git() download handlers.
            git("fetch", "origin", "pull/17/head:clang")
            git("checkout", "clang")
            #            

            make_ = run.watch(make)
            make_("config")

            clang = compiler.cc(self)
            clang_cxx = compiler.cxx(self)

            make_("CC=" + str(clang), "CXX=" + str(clang_cxx), "clean", "lsh",
                  "sh")
