from os import path

from plumbum import local

import benchbuild as bb
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.source import HTTP
from benchbuild.utils.cmd import make, mkdir, tar


class TCC(bb.Project):
    VERSION = '0.9.26'
    NAME = 'tcc'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    SOURCE = [
        HTTP(
            remote={
                '0.9.26': (
                    'http://download-mirror.savannah.gnu.org/releases/'
                    'tinycc/tcc-0.9.26.tar.bz2'
                )
            },
            local='tcc.tar.bz2'
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def compile(self):
        tcc_source = local.path(self.source_of('tcc.tar.bz2'))
        tcc_version = self.version_of('tcc.tar.bz2')

        tar("xf", tcc_source)
        unpack_dir = local.path(f'tcc-{tcc_version}.tar.bz2')

        clang = bb.compiler.cc(self)

        with local.cwd(unpack_dir):
            mkdir("build")
            with local.cwd("build"):
                configure = local["../configure"]
                _configure = bb.watch(configure)
                _configure("--cc=" + str(clang), "--with-libgcc")

                _make = bb.watch(make)
                _make()

    def run_tests(self):
        tcc_version = self.version_of('tcc.tar.bz2')
        unpack_dir = local.path(f'tcc-{tcc_version}.tar.bz2')
        with local.cwd(unpack_dir):
            with local.cwd("build"):
                bb.wrap("tcc", self)
                inc_path = path.abspath("..")
                _make = bb.watch(make)
                _make("TCCFLAGS=-B{}".format(inc_path), "test", "-i")
