from plumbum import local

from benchbuild import project
from benchbuild.downloads import Git
from benchbuild.utils import compiler, run, wrapping


class Lulesh(project.Project):
    """ LULESH, Serial """

    NAME = 'lulesh'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    VERSION = 'HEAD'
    SOURCE = [
        Git(remote='https://github.com/LLNL/LULESH/',
            local='lulesh.git',
            limit=5,
            refspec='HEAD')
    ]

    def compile(self):
        lulesh_repo = local.path(self.source[0].local)
        self.cflags += ["-DUSE_MPI=0"]

        cxx_files = local.cwd / lulesh_repo// "*.cc"
        clang = compiler.cxx(self)
        with local.cwd(lulesh_repo):
            for src_file in cxx_files:
                clang("-c", "-o", src_file + '.o', src_file)

        obj_files = local.cwd / lulesh_repo // "*.cc.o"
        with local.cwd(lulesh_repo):
            clang(obj_files, "-lm", "-o", "../lulesh")

    def run_tests(self):
        lulesh = wrapping.wrap("lulesh", self)
        lulesh = run.watch(lulesh)

        for i in range(1, 15):
            lulesh("-i", i)


class LuleshOMP(project.Project):
    """ LULESH, OpenMP """

    NAME = 'lulesh-omp'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    VERSION = 'HEAD'
    SOURCE = [
        Git(remote='https://github.com/LLNL/LULESH/',
            local='lulesh.git',
            limit=5,
            refspec='HEAD')
    ]

    def compile(self):
        lulesh_repo = local.path(self.source[0].local)
        self.cflags = ['-DUSE_MPI=0', '-fopenmp']

        cxx_files = local.cwd / lulesh_repo // "*.cc"
        clang = compiler.cxx(self)
        with local.cwd(lulesh_repo):
            for src_file in cxx_files:
                clang("-c", "-o", src_file + '.o', src_file)

        obj_files = local.cwd / lulesh_repo // "*.cc.o"
        with local.cwd(lulesh_repo):
            clang(obj_files, "-lm", "-o", "../lulesh")

    def run_tests(self):
        lulesh = wrapping.wrap("lulesh", self)
        lulesh = run.watch(lulesh)
        for i in range(1, 15):
            lulesh("-i", i)
