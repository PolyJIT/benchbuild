import benchbuild as bb
from benchbuild.utils import download


@download.with_git("https://github.com/LLNL/LULESH/", limit=5)
class Lulesh(bb.Project):
    """ LULESH, Serial """

    NAME = 'lulesh'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SRC_FILE = 'lulesh.git'
    VERSION = 'HEAD'

    def compile(self):
        self.download()
        self.cflags += ["-DUSE_MPI=0"]

        cxx_files = bb.cwd / self.src_file // "*.cc"
        with bb.cwd(self.src_file):
            clang = bb.compiler.cxx(self)
            for src_file in cxx_files:
                clang("-c", "-o", src_file + '.o', src_file)

        obj_files = bb.cwd / self.src_file // "*.cc.o"
        with bb.cwd(self.src_file):
            clang(obj_files, "-lm", "-o", "../lulesh")

    def run_tests(self):
        lulesh = bb.wrap("lulesh", self)
        _lulesh = bb.watch(lulesh)

        for i in range(1, 15):
            _lulesh("-i", i)


@download.with_git("https://github.com/LLNL/LULESH/", limit=5)
class LuleshOMP(bb.Project):
    """ LULESH, OpenMP """

    NAME = 'lulesh-omp'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SRC_FILE = 'lulesh.git'
    VERSION = 'HEAD'

    def compile(self):
        self.download()
        self.cflags = ['-DUSE_MPI=0', '-fopenmp']

        cxx_files = bb.cwd / self.src_file // "*.cc"
        with bb.cwd(self.src_file):
            clang = bb.compiler.cxx(self)
            for src_file in cxx_files:
                clang("-c", "-o", src_file + '.o', src_file)

        obj_files = bb.cwd / self.src_file // "*.cc.o"
        with bb.cwd(self.src_file):
            clang(obj_files, "-lm", "-o", "../lulesh")

    def run_tests(self):
        lulesh = bb.wrap("lulesh", self)
        _lulesh = bb.watch(lulesh)
        for i in range(1, 15):
            _lulesh("-i", i)
