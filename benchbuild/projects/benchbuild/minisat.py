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

    def run_tests(self, runner):
        src_path = local.path(self.src_file)
        minisat_lib_path = src_path / "build" / "dynamic" / "lib"
        testfiles = local.path(self.testdir) // "*.cnf.gz"

        minisat = wrapping.wrap(
            src_path / "build" / "dynamic" / "bin" / "minisat", self)
        for test_f in testfiles:
            cmd = (minisat.with_env(LD_LIBRARY_PATH=minisat_lib_path) < test_f)
            runner(cmd, None)

    def compile(self):
        self.download()
        with local.cwd(self.src_file):
            git("fetch", "origin", "pull/17/head:clang")
            git("checkout", "clang")

            run.run(make["config"])

            clang = compiler.cc(self)
            clang_cxx = compiler.cxx(self)
            run.run(make["CC=" + str(clang), "CXX=" +
                         str(clang_cxx), "clean", "lsh", "sh"])
