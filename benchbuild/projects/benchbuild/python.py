from plumbum import local

import benchbuild as bb
from benchbuild.environments import Buildah
from benchbuild.source import HTTP
from benchbuild.utils.cmd import make, tar


class Python(bb.Project):
    """ python benchmarks """

    NAME = 'python'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    SOURCE = [
        HTTP(remote={
            '3.4.3':
                'https://www.python.org/ftp/python/3.4.3/Python-3.4.3.tar.xz'
        },
             local='python.tar.xz')
    ]
    CONTAINER = Buildah().from_('benchbuild:alpine')

    def compile(self):
        python_source = bb.path(self.source_of('python.tar.xz'))
        python_version = self.version_of('python.tar.xz')

        tar("xfJ", python_source)
        unpack_dir = bb.path(f'Python-{python_version}')

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
        python_version = self.version_of('python.tar.xz')
        unpack_dir = bb.path(f'Python-{python_version}')
        bb.wrap(unpack_dir / "python", self)

        with bb.cwd(unpack_dir):
            _make = bb.watch(make)
            _make("-i", "test")
