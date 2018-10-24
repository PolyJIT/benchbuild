from plumbum import local

from benchbuild import project
from benchbuild.utils import compiler, download, wrapping


@download.with_git("https://github.com/LLNL/LULESH/", limit=5)
class Lulesh(project.Project):
    """ LULESH, Serial """

    NAME = 'lulesh'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SRC_FILE = 'lulesh.git'
    VERSION = 'HEAD'

    def compile(self):
        self.download()
        self.cflags += ["-DUSE_MPI=0"]

        cxx_files = local.cwd / self.src_file // "*.cc"
        clang = compiler.cxx(self)
        with local.cwd(self.src_file):
            for src_file in cxx_files:
                clang("-c", "-o", src_file + '.o', src_file)

        obj_files = local.cwd / self.src_file // "*.cc.o"
        with local.cwd(self.src_file):
            clang(obj_files, "-lm", "-o", "../lulesh")

    def run_tests(self, runner):
        lulesh = wrapping.wrap("lulesh", self)
        for i in range(1, 15):
            runner(lulesh["-i", i])


@download.with_git("https://github.com/LLNL/LULESH/", limit=5)
class LuleshOMP(project.Project):
    """ LULESH, OpenMP """

    NAME = 'lulesh-omp'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SRC_FILE = 'lulesh.git'
    VERSION = 'HEAD'

    def compile(self):
        self.download()
        self.cflags = ['-DUSE_MPI=0', '-fopenmp']

        cxx_files = local.cwd / self.src_file // "*.cc"
        clang = compiler.cxx(self)
        with local.cwd(self.src_file):
            for src_file in cxx_files:
                clang("-c", "-o", src_file + '.o', src_file)

        obj_files = local.cwd / self.src_file // "*.cc.o"
        with local.cwd(self.src_file):
            clang(obj_files, "-lm", "-o", "../lulesh")

    def run_tests(self, runner):
        lulesh = wrapping.wrap("lulesh", self)
        for i in range(1, 15):
            runner(lulesh["-i", i])
