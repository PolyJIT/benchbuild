from plumbum import local

from benchbuild import project
from benchbuild.settings import CFG
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import make
from benchbuild.utils.settings import get_number_of_jobs


class SDCC(project.Project):
    NAME = 'sdcc'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    SRC_FILE = 'sdcc'

    src_uri = "svn://svn.code.sf.net/p/sdcc/code/trunk/" + SRC_FILE

    def compile(self):
        download.Svn(self.src_uri, self.SRC_FILE)

        clang = compiler.cc(self)
        clang_cxx = compiler.cxx(self)

        with local.cwd(self.SRC_FILE):
            configure = local["./configure"]
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                run.run(configure["--without-ccache", "--disable-pic14-port",
                                  "--disable-pic16-port"])

            run.run(make["-j", get_number_of_jobs(CFG)])

    def run_tests(self, runner):
        sdcc = wrapping.wrap(self.run_f, self)
        runner(sdcc)
