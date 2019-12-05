from os import path

from plumbum import local

import benchbuild as bb

from benchbuild.downloads import HTTP
from benchbuild.utils.cmd import make, mkdir, tar


class TCC(bb.Project):
    NAME: str = 'tcc'
    DOMAIN: str = 'compilation'
    GROUP: str = 'benchbuild'
    VERSION: str = '0.9.26'
    SOURCE: str = [
        HTTP(remote={
            '0.9.26':
            'http://download-mirror.savannah.gnu.org/releases/tinycc/tcc-0.9.26.tar.bz2'
        },
             local='tcc.tar.bz2')
    ]

    def compile(self):
        tcc_source = bb.path(self.source[0].local)
        tcc_source = bb.path(self.source_of('tcc.tar.bz2'))
        tar("xf", tcc_source)
        unpack_dir = bb.path('tcc-{0}.tar.bz2'.format(self.version))

        clang = bb.compiler.cc(self)

        with bb.cwd(unpack_dir):
            mkdir("build")
            with local.cwd("build"):
                configure = local["../configure"]
                confiugre = bb.watch(configure)
                configure("--cc=" + str(clang), "--with-libgcc")

                make_ = bb.watch(make)
                make_()

    def run_tests(self, runner):
        unpack_dir = local.path('tcc-{0}.tar.bz2'.format(self.version))
        with local.cwd(unpack_dir):
            with local.cwd("build"):
                bb.wrap("tcc", self)
                inc_path = path.abspath("..")
                make_ = bb.watch(make)
                make_("TCCFLAGS=-B{}".format(inc_path), "test", "-i")
