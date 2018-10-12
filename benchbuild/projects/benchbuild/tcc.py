from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import make, mkdir, tar
from benchbuild.utils.compiler import cc
from benchbuild.utils.downloader import with_wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


@with_wget({
    '0.9.26':
    'http://download-mirror.savannah.gnu.org/releases/tinycc/tcc-0.9.26.tar.bz2'
})
class TCC(Project):
    NAME = 'tcc'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    VERSION = '0.9.26'
    SRC_FILE = 'tcc.tar.bz2'

    def compile(self):
        self.download()

        tar("xf", self.src_file)
        unpack_dir = local.path('tcc-{0}.tar.bz2'.format(self.version))

        clang = cc(self)

        with local.cwd(unpack_dir):
            mkdir("build")
            with local.cwd("build"):
                configure = local["../configure"]
                run(configure["--cc=" + str(clang), "--with-libgcc"])
                run(make)

    def run_tests(self, runner):
        unpack_dir = local.path('tcc-{0}.tar.bz2'.format(self.version))
        with local.cwd(unpack_dir):
            with local.cwd("build"):
                wrap("tcc", self)
                inc_path = path.abspath("..")
                run(make["TCCFLAGS=-B{}".format(inc_path), "test", "-i"])
