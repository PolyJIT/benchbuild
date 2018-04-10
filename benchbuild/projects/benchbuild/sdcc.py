from plumbum import local

from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.cmd import make
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.downloader import Svn
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


class SDCC(Project):
    NAME = 'sdcc'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    SRC_FILE = 'sdcc'

    src_uri = "svn://svn.code.sf.net/p/sdcc/code/trunk/" + SRC_FILE

    def download(self):
        Svn(self.src_uri, self.SRC_FILE)

    def configure(self):
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)

        with local.cwd(self.SRC_FILE):
            configure = local["./configure"]
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                run(configure["--without-ccache", "--disable-pic14-port",
                              "--disable-pic16-port"])

    def build(self):
        with local.cwd(self.SRC_FILE):
            run(make["-j", CFG["jobs"]])

    def run_tests(self, experiment, runner):
        exp = wrap(self.run_f, experiment(self.run_f))
        runner(exp)
