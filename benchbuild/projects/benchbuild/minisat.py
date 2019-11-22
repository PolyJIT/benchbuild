from plumbum import local

from benchbuild import project
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import git, make


@download.with_git("https://github.com/niklasso/minisat", limit=5)
class Minisat(project.Project):
    """ minisat benchmark """

    NAME = 'minisat'
    DOMAIN = 'verification'
    GROUP = 'benchbuild'
    SRC_FILE = 'minisat.git'
    VERSION = 'HEAD'

    def run_tests(self):
        src_path = local.path(self.src_file)
        minisat_lib_path = src_path / "build" / "dynamic" / "lib"
        testfiles = local.path(self.testdir) // "*.cnf.gz"

        minisat = wrapping.wrap(
            src_path / "build" / "dynamic" / "bin" / "minisat", self)
        for test_f in testfiles:
            minisat_test = run.watch(
                (minisat.with_env(LD_LIBRARY_PATH=minisat_lib_path) < test_f))
            minisat_test()

    def compile(self):
        self.download()
        with local.cwd(self.src_file):
            git("fetch", "origin", "pull/17/head:clang")
            git("checkout", "clang")

            make_ = run.watch(make)
            make_("config")

            clang = compiler.cc(self)
            clang_cxx = compiler.cxx(self)

            make_("CC=" + str(clang), "CXX=" + str(clang_cxx), "clean", "lsh",
                  "sh")
