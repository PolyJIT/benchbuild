from plumbum import local

import benchbuild as bb
from benchbuild.settings import CFG
from benchbuild.utils.cmd import make


class SDCC(bb.Project):
    NAME = 'sdcc'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    SRC_FILE = 'sdcc'

    src_uri = "svn://svn.code.sf.net/p/sdcc/code/trunk/" + SRC_FILE

    def compile(self):
        bb.download.Svn(self.src_uri, self.SRC_FILE)

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)

        with bb.cwd(self.SRC_FILE):
            configure = local["./configure"]
            configure = bb.watch(configure)
            with bb.env(CC=str(clang), CXX=str(clang_cxx)):
                configure("--without-ccache", "--disable-pic14-port",
                          "--disable-pic16-port")

            make_ = bb.watch(make)
            make_("-j", CFG["jobs"])

    def run_tests(self):
        sdcc = bb.wrap('sdcc', self)
        sdcc = bb.watch(sdcc)
        sdcc()
