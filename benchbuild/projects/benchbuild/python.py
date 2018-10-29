from plumbum import local

from benchbuild import project
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import make, tar


@download.with_wget({
    '3.4.3':
    'https://www.python.org/ftp/python/3.4.3/Python-3.4.3.tar.xz'
})
class Python(project.Project):
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

        clang = compiler.cc(self)
        clang_cxx = compiler.cxx(self)

        with local.cwd(unpack_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                run.run(configure["--disable-shared", "--without-gcc"])

            run.run(make)

    def run_tests(self, runner):
        unpack_dir = local.path('Python-{0}'.format(self.version))
        wrapping.wrap(unpack_dir / "python", self)

        with local.cwd(unpack_dir):
            runner(make["-i", "test"])
