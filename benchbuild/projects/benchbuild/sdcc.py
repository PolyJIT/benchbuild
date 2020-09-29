from plumbum import local

import benchbuild as bb
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.settings import CFG
from benchbuild.utils.cmd import make
from benchbuild.utils.settings import get_number_of_jobs


class SDCC(bb.Project):
    NAME = 'sdcc'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    SRC_FILE = 'sdcc'
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    src_uri = "svn://svn.code.sf.net/p/sdcc/code/trunk/" + SRC_FILE

    def compile(self):
        bb.download.Svn(self.src_uri, self.SRC_FILE)

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)

        with local.cwd(self.SRC_FILE):
            configure = local["./configure"]
            _configure = bb.watch(configure)
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                _configure(
                    "--without-ccache", "--disable-pic14-port",
                    "--disable-pic16-port"
                )

            _make = bb.watch(make)
            _make("-j", get_number_of_jobs(CFG))

    def run_tests(self):
        sdcc = bb.wrap('sdcc', self)
        _sdcc = bb.watch(sdcc)
        _sdcc()
