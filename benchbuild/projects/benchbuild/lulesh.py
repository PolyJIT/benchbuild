from benchbuild.utils.wrapping import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang_cxx
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run


class Lulesh(BenchBuildGroup):
    """ Lulesh """

    NAME = 'lulesh'
    DOMAIN = 'scientific'
    SRC_FILE = 'LULESH.cc'

    def run_tests(self, experiment, run):
        exp = wrap(self.run_f, experiment)
        for i in range(1, 15):
            run(exp[str(i)])

    src_uri = "https://codesign.llnl.gov/lulesh/" + SRC_FILE

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)

    def configure(self):
        pass

    def build(self):
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)
        run(clang_cxx["-o", self.run_f, self.SRC_FILE])
