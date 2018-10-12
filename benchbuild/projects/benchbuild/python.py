from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import make, tar
from benchbuild.utils.compiler import cc, cxx
from benchbuild.utils.downloader import with_wget, Wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


@with_wget({
    '3.4.3':
    'https://www.python.org/ftp/python/3.4.3/Python-3.4.3.tar.xz'
})
class Python(Project):
    """ python benchmarks """

    NAME = 'python'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    VERSION = '3.4.3'
    SRC_FILE = 'python.tar.xz'

    def compile(self):
        self.download()
        tar("xfJ", self.src_file)
        unpack_dir = local.path('Python-{0}'.format(self.version))

        clang = cc(self)
        clang_cxx = cxx(self)

        with local.cwd(unpack_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                run(configure["--disable-shared", "--without-gcc"])

            run(make)

    def run_tests(self, runner):
        unpack_dir = local.path('Python-{0}'.format(self.version))
        wrap(unpack_dir / "python", self)

        with local.cwd(unpack_dir):
            run(make["-i", "test"])
