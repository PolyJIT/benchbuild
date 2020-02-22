from plumbum import local

from benchbuild.environments import container

from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.cmd import make


class SDCC(Project):
    NAME = 'sdcc'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    SRC_FILE = 'sdcc'
    CONTAINER = container.Buildah().from_('debian:buster-slim')

    src_uri = "svn://svn.code.sf.net/p/sdcc/code/trunk/" + SRC_FILE

    def compile(self):
        bb.download.Svn(self.src_uri, self.SRC_FILE)

        clang = compiler.cc(self)
        clang_cxx = compiler.cxx(self)

        with local.cwd(self.SRC_FILE):
            configure = local["./configure"]
            configure = run.watch(configure)
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                configure("--without-ccache", "--disable-pic14-port",
                          "--disable-pic16-port")

            make_ = run.watch(make)
            make_("-j", CFG["jobs"])

    def run_tests(self):
        sdcc = wrapping.wrap('sdcc', self)
        sdcc = run.watch(sdcc)
        sdcc()
