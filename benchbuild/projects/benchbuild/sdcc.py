from plumbum import local

from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.cmd import make
from benchbuild.utils.compiler import cc, cxx
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
        clang = cc(self)
        clang_cxx = cxx(self)

        with local.cwd(self.SRC_FILE):
            configure = local["./configure"]
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                run(configure["--without-ccache", "--disable-pic14-port",
                              "--disable-pic16-port"])

    def build(self):
        with local.cwd(self.SRC_FILE):
            run(make["-j", CFG["jobs"]])

    def run_tests(self, runner):
        exp = wrap(self.run_f, self)
        runner(exp)
