from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.environments import container
from benchbuild.source import HTTP
from benchbuild.utils.cmd import make, mkdir, tar


class TCC(Project):
    NAME: str = 'tcc'
    DOMAIN: str = 'compilation'
    GROUP: str = 'benchbuild'
    SOURCE: str = [
        HTTP(remote={
            '0.9.26':
            'http://download-mirror.savannah.gnu.org/releases/tinycc/tcc-0.9.26.tar.bz2'
        },
             local='tcc.tar.bz2')
    ]
    CONTAINER = container.Buildah().from_('debian:buster-slim')

    def compile(self):
        tcc_source = local.path(self.source_of('tcc.tar.bz2'))
        tcc_version = self.version_of('tcc.tar.bz2')

        tar("xf", tcc_source)
        unpack_dir = local.path(f'tcc-{tcc_version}.tar.bz2')

        clang = compiler.cc(self)

        with local.cwd(unpack_dir):
            mkdir("build")
            with local.cwd("build"):
                configure = local["../configure"]
                configure = run.watch(configure)
                configure("--cc=" + str(clang), "--with-libgcc")

                make_ = run.watch(make)
                make_()

    def run_tests(self, runner):
        tcc_version = self.version_of('tcc.tar.bz2')
        unpack_dir = local.path(f'tcc-{tcc_version}.tar.bz2')
        with local.cwd(unpack_dir):
            with local.cwd("build"):
                wrapping.wrap("tcc", self)
                inc_path = path.abspath("..")
                make_ = run.watch(make)
                make_("TCCFLAGS=-B{}".format(inc_path), "test", "-i")
