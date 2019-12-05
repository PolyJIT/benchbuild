from os import path

from plumbum import local

from benchbuild import project
from benchbuild.downloads import HTTP
from benchbuild.utils import compiler, run, wrapping
from benchbuild.utils.cmd import make, mkdir, tar


class TCC(project.Project):
    VERSION = '0.9.26'
    SOURCE = [
    NAME: str = 'tcc'
    DOMAIN: str = 'compilation'
    GROUP: str = 'benchbuild'
        HTTP(remote={
            '0.9.26':
            'http://download-mirror.savannah.gnu.org/releases/tinycc/tcc-0.9.26.tar.bz2'
        },
             local='tcc.tar.bz2')
    ]

    def compile(self):
        tcc_source = local.path(self.source[0].local)
        tar("xf", tcc_source)
        unpack_dir = local.path('tcc-{0}.tar.bz2'.format(self.version))

        clang = compiler.cc(self)

        with local.cwd(unpack_dir):
            mkdir("build")
            with local.cwd("build"):
                configure = local["../configure"]
                confiugre = run.watch(configure)
                configure("--cc=" + str(clang), "--with-libgcc")

                make_ = run.watch(make)
                make_()

    def run_tests(self, runner):
        unpack_dir = local.path('tcc-{0}.tar.bz2'.format(self.version))
        with local.cwd(unpack_dir):
            with local.cwd("build"):
                wrapping.wrap("tcc", self)
                inc_path = path.abspath("..")
                make_ = run.watch(make)
                make_("TCCFLAGS=-B{}".format(inc_path), "test", "-i")
