from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import git, make
from benchbuild.utils.compiler import cc, cxx
from benchbuild.utils.downloader import with_git
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


@with_git("https://github.com/niklasso/minisat", limit=5)
class Minisat(Project):
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

        exp = wrap(src_path / "build" / "dynamic" / "bin" / "minisat", self)
        for test_f in testfiles:
            cmd = (exp.with_env(LD_LIBRARY_PATH=minisat_lib_path) < test_f)
            runner(cmd, None)

    def compile(self):
        self.download()
        with local.cwd(self.src_file):
            git("fetch", "origin", "pull/17/head:clang")
            git("checkout", "clang")

            run(make["config"])

            clang = cc(self)
            clang_cxx = cxx(self)
            run(make["CC=" + str(clang), "CXX=" +
                     str(clang_cxx), "clean", "lsh", "sh"])
