from pprof.projects.pprof.group import PprofGroup
from plumbum import local


class Lulesh(PprofGroup):
    """ Lulesh """

    NAME = 'lulesh'
    DOMAIN = 'scientific'

    def run_tests(self, experiment):
        from pprof.project import wrap
        from pprof.utils.run import run

        exp = wrap(self.run_f, experiment)
        for i in range(1, 15):
            run(exp[str(i)])

    src_file = "LULESH.cc"
    src_uri = "https://codesign.llnl.gov/lulesh/" + src_file

    def download(self):
        from pprof.utils.downloader import Wget

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)

    def configure(self):
        pass

    def build(self):
        from pprof.utils.compiler import lt_clang_cxx
        from pprof.utils.run import run

        with local.cwd(self.builddir):
            clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                     self.compiler_extension)
            run(clang_cxx["-o", self.run_f, self.src_file])
