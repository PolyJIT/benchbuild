from os import path

from plumbum import local

import benchbuild as bb
from benchbuild.utils import download
from benchbuild.utils.cmd import make, mkdir, tar


@download.with_wget({
    '0.9.26':
        'http://download-mirror.savannah.gnu.org/releases/tinycc/tcc-0.9.26.tar.bz2'
})
class TCC(bb.Project):
    NAME = 'tcc'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    VERSION = '0.9.26'
    SRC_FILE = 'tcc.tar.bz2'

    def compile(self):
        self.download()

        tar("xf", self.src_file)
        unpack_dir = bb.path('tcc-{0}.tar.bz2'.format(self.version))

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
        unpack_dir = bb.path('tcc-{0}.tar.bz2'.format(self.version))
        with bb.cwd(unpack_dir):
            with bb.cwd("build"):
                bb.wrap("tcc", self)
                inc_path = path.abspath("..")
                _make = bb.watch(make)
                _make("TCCFLAGS=-B{}".format(inc_path), "test", "-i")
