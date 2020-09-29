from plumbum import local

import benchbuild as bb
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.source import Git


class Lulesh(bb.Project):
    """ LULESH, Serial """

    NAME = 'lulesh'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SOURCE = [
        Git(
            remote='https://github.com/LLNL/LULESH/',
            local='lulesh.git',
            limit=5,
            refspec='HEAD'
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def compile(self):
        lulesh_repo = local.path(self.source_of('lulesh.git'))
        self.cflags += ["-DUSE_MPI=0"]

        cxx_files = local.cwd / lulesh_repo // "*.cc"
        clang = bb.compiler.cxx(self)
        with local.cwd(lulesh_repo):
            for src_file in cxx_files:
                clang("-c", "-o", src_file + '.o', src_file)

        obj_files = local.cwd / lulesh_repo // "*.cc.o"
        with local.cwd(lulesh_repo):
            clang(obj_files, "-lm", "-o", "../lulesh")

    def run_tests(self):
        lulesh = bb.wrap("lulesh", self)
        _lulesh = bb.watch(lulesh)

        for i in range(1, 15):
            _lulesh("-i", i)


class LuleshOMP(bb.Project):
    """ LULESH, OpenMP """

    NAME = 'lulesh-omp'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SOURCE = [
        Git(
            remote='https://github.com/LLNL/LULESH/',
            local='lulesh.git',
            limit=5,
            refspec='HEAD'
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def compile(self):
        lulesh_repo = local.path(self.source_of('lulesh.git'))
        self.cflags = ['-DUSE_MPI=0', '-fopenmp']

        cxx_files = local.cwd / lulesh_repo // "*.cc"
        clang = bb.compiler.cxx(self)
        with local.cwd(lulesh_repo):
            for src_file in cxx_files:
                clang("-c", "-o", src_file + '.o', src_file)

        obj_files = local.cwd / lulesh_repo // "*.cc.o"
        with local.cwd(lulesh_repo):
            clang(obj_files, "-lm", "-o", "../lulesh")

    def run_tests(self):
        lulesh = bb.wrap("lulesh", self)
        _lulesh = bb.watch(lulesh)
        for i in range(1, 15):
            _lulesh("-i", i)
