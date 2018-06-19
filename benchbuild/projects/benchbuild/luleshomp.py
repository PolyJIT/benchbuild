from benchbuild.project import Project
from benchbuild.utils.compiler import cxx
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


class LuleshOMP(Project):
    """ Lulesh-OMP """

    NAME = 'lulesh-omp'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SRC_FILE = 'LULESH_OMP.cc'

    def run_tests(self, runner):
        exp = wrap(self.run_f, self)
        for i in range(1, 15):
            runner(exp[str(i)])

    src_uri = "https://codesign.llnl.gov/lulesh/" + SRC_FILE

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)

    def configure(self):
        pass

    def build(self):
        """
        Build process for OpenMP enabled LULESH code:

        Required: openmp (omp.h) needs to be available.
        """
        self.cflags += ["-fopenmp"]

        clang_cxx = cxx(self)
        run(clang_cxx["-o", self.run_f, self.SRC_FILE])
