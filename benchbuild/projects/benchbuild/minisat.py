from glob import glob
from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import git, make
from benchbuild.utils.compiler import cc, cxx
from benchbuild.utils.downloader import Git
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


class Minisat(Project):
    """ minisat benchmark """

    NAME = 'minisat'
    DOMAIN = 'verification'
    GROUP = 'benchbuild'
    SRC_FILE = 'minisat.git'

    def run_tests(self, runner):
        minisat_lib_path = path.abspath(path.join(
            self.SRC_FILE, "build", "dynamic", "lib"))

        exp = wrap(
            path.join(self.SRC_FILE, "build", "dynamic", "bin", "minisat"),
            self)

        testfiles = glob(path.join(self.testdir, "*.cnf.gz"))

        for test_f in testfiles:
            cmd = (exp.with_env(LD_LIBRARY_PATH=minisat_lib_path) < test_f)
            runner(cmd, None)

    src_uri = "https://github.com/niklasso/minisat"

    def download(self):
        Git(self.src_uri, self.SRC_FILE)
        with local.cwd(self.SRC_FILE):
            git("fetch", "origin", "pull/17/head:clang")
            git("checkout", "clang")

    def configure(self):
        with local.cwd(self.SRC_FILE):
            run(make["config"])

    def build(self):
        with local.cwd(self.SRC_FILE):
            clang = cc(self)
            clang_cxx = cxx(self)
            run(make["CC=" + str(clang), "CXX=" + str(clang_cxx), "clean",
                     "lsh", "sh"])
