from plumbum import local

from benchbuild.project import Project
from benchbuild.environments import container
from benchbuild.source import HTTP
from benchbuild.utils.cmd import make, tar


class Python(Project):
    """ python benchmarks """

    NAME: str = 'python'
    DOMAIN: str = 'compilation'
    GROUP: str = 'benchbuild'
    SOURCE = [
        HTTP(remote={
            '3.4.3':
            'https://www.python.org/ftp/python/3.4.3/Python-3.4.3.tar.xz'
        },
             local='python.tar.xz')
    ]
    CONTAINER = container.Buildah().from_('debian:buster-slim')

    def compile(self):
        python_source = local.path(self.source_of('python.tar.xz'))
        python_version = self.version_of('python.tar.xz')

        tar("xfJ", python_source)
        unpack_dir = local.path(f'Python-{python_version}')

        clang = compiler.cc(self)
        clang_cxx = compiler.cxx(self)

        with local.cwd(unpack_dir):
            configure = local["./configure"]
            configure = run.watch(configure)
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                configure("--disable-shared", "--without-gcc")

            make_ = run.watch(make)
            make_()

    def run_tests(self):
        python_version = self.version_of('python.tar.xz')
        unpack_dir = local.path(f'Python-{python_version}')
        wrapping.wrap(unpack_dir / "python", self)

        with local.cwd(unpack_dir):
            make_ = run.watch(make)
            make_("-i", "test")
