from plumbum import local

import benchbuild as bb
from benchbuild.utils import download
from benchbuild.utils.cmd import make, tar


@download.with_wget(
    {'3.4.3': 'https://www.python.org/ftp/python/3.4.3/Python-3.4.3.tar.xz'})
class Python(bb.Project):
    """ python benchmarks """

    NAME = 'python'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    VERSION = '3.4.3'
    SRC_FILE = 'python.tar.xz'

    def compile(self):
        self.download()
        tar("xfJ", self.src_file)
        unpack_dir = bb.path('Python-{0}'.format(self.version))

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)

        with bb.cwd(unpack_dir):
            configure = local["./configure"]
            configure = bb.watch(configure)
            with bb.env(CC=str(clang), CXX=str(clang_cxx)):
                configure("--disable-shared", "--without-gcc")

            _make = bb.watch(make)
            _make()

    def run_tests(self):
        unpack_dir = bb.path('Python-{0}'.format(self.version))
        bb.wrap(unpack_dir / "python", self)

        with bb.cwd(unpack_dir):
            _make = bb.watch(make)
            _make("-i", "test")
