from os import path

from plumbum import local

from benchbuild import project
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import make, mkdir, tar


@download.with_wget({
    '0.9.26':
    'http://download-mirror.savannah.gnu.org/releases/tinycc/tcc-0.9.26.tar.bz2'
})
class TCC(project.Project):
    NAME = 'tcc'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    VERSION = '0.9.26'
    SRC_FILE = 'tcc.tar.bz2'

    def compile(self):
        self.download()

        tar("xf", self.src_file)
        unpack_dir = local.path('tcc-{0}.tar.bz2'.format(self.version))

        clang = compiler.cc(self)

        with local.cwd(unpack_dir):
            mkdir("build")
            with local.cwd("build"):
                configure = local["../configure"]
                run.run(configure["--cc=" + str(clang), "--with-libgcc"])
                run.run(make)

    def run_tests(self, runner):
        unpack_dir = local.path('tcc-{0}.tar.bz2'.format(self.version))
        with local.cwd(unpack_dir):
            with local.cwd("build"):
                wrapping.wrap("tcc", self)
                inc_path = path.abspath("..")
                runner(make["TCCFLAGS=-B{}".format(inc_path), "test", "-i"])
