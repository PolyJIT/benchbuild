from os import path

from plumbum import local

import benchbuild as bb
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
                '0.9.26':
                    'http://download-mirror.savannah.gnu.org/releases/tinycc/tcc-0.9.26.tar.bz2'  # pylint: disable=line-too-long
            },
            local='tcc.tar.bz2')
    ]

    def compile(self):
        tcc_source = bb.path(self.source_of('tcc.tar.bz2'))
        tcc_version = self.version_of('tcc.tar.bz2')

        tar("xf", tcc_source)
        unpack_dir = bb.path(f'tcc-{tcc_version}.tar.bz2')

        clang = bb.compiler.cc(self)

        with bb.cwd(unpack_dir):
            mkdir("build")
            with bb.cwd("build"):
                configure = local["../configure"]
                _configure = bb.watch(configure)
                _configure("--cc=" + str(clang), "--with-libgcc")

                _make = bb.watch(make)
                _make()

    def run_tests(self):
        tcc_version = self.version_of('tcc.tar.bz2')
        unpack_dir = bb.path(f'tcc-{tcc_version}.tar.bz2')
        with bb.cwd(unpack_dir):
            with bb.cwd("build"):
                bb.wrap("tcc", self)
                inc_path = path.abspath("..")
                _make = bb.watch(make)
                _make("TCCFLAGS=-B{}".format(inc_path), "test", "-i")
