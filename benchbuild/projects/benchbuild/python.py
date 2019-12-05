from plumbum import local

from benchbuild import project
from benchbuild.downloads import HTTP
from benchbuild.utils import compiler, run, wrapping
from benchbuild.utils.cmd import make, tar


class Python(project.Project):
    """ python benchmarks """

    VERSION = '3.4.3'
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

    def compile(self):
        python_source = local.path(self.source[0].local)

        tar("xfJ", python_source)
        unpack_dir = local.path('Python-{0}'.format(self.version))

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
        unpack_dir = local.path('Python-{0}'.format(self.version))
        wrapping.wrap(unpack_dir / "python", self)

        with local.cwd(unpack_dir):
            make_ = run.watch(make)
            make_("-i", "test")
