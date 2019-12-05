from plumbum import local

import benchbuild as bb

from benchbuild.downloads import HTTP
from benchbuild.utils.cmd import make, tar


class Python(bb.Project):
    """ python benchmarks """

    NAME: str = 'python'
    DOMAIN: str = 'compilation'
    GROUP: str = 'benchbuild'
    VERSION: str = '3.4.3'
    SOURCE = [
        HTTP(remote={
            '3.4.3':
            'https://www.python.org/ftp/python/3.4.3/Python-3.4.3.tar.xz'
        },
             local='python.tar.xz')
    ]

    def compile(self):
        python_source = bb.path(bb.to_source('python.tar.xz'))

        tar("xfJ", python_source)
        unpack_dir = bb.path('Python-{0}'.format(self.version))

        clang = bb.compiler.cc(self)
        clang_cxx = bb.compiler.cxx(self)

        with local.cwd(unpack_dir):
            configure = local["./configure"]
            configure = bb.watch(configure)
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                configure("--disable-shared", "--without-gcc")

            make_ = bb.watch(make)
            make_()

    def run_tests(self):
        unpack_dir = bb.path('Python-{0}'.format(self.version))
        bb.wrap(unpack_dir / "python", self)

        with bb.cwd(unpack_dir):
            make_ = bb.watch(make)
            make_("-i", "test")
