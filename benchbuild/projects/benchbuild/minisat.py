import benchbuild as bb
from benchbuild.utils import download
from benchbuild.utils.cmd import git, make


@download.with_git("https://github.com/niklasso/minisat", limit=5)
class Minisat(bb.Project):
    """ minisat benchmark """

    NAME = 'minisat'
    DOMAIN = 'verification'
    GROUP = 'benchbuild'
    SRC_FILE = 'minisat.git'
    VERSION = 'HEAD'

    def run_tests(self):
        src_path = bb.path(self.src_file)
        minisat_lib_path = src_path / "build" / "dynamic" / "lib"
        testfiles = bb.path(self.testdir) // "*.cnf.gz"

        minisat = bb.wrap(src_path / "build" / "dynamic" / "bin" / "minisat",
                          self)
        for test_f in testfiles:
            _minisat = bb.watch(
                (minisat.with_env(LD_LIBRARY_PATH=minisat_lib_path) < test_f))
            _minisat()

    def compile(self):
        self.download()
        with bb.cwd(self.src_file):
            git("fetch", "origin", "pull/17/head:clang")
            git("checkout", "clang")

            _make = bb.watch(make)
            _make("config")

            clang = bb.compiler.cc(self)
            clang_cxx = bb.compiler.cxx(self)

            _make("CC=" + str(clang), "CXX=" + str(clang_cxx), "clean", "lsh",
                  "sh")
