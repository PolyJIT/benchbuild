from plumbum import local

from benchbuild.project import Project
from benchbuild.environments import container

from benchbuild.source import Git


class Lulesh(Project):
    """ LULESH, Serial """

    NAME: str = 'lulesh'
    DOMAIN: str = 'scientific'
    GROUP: str = 'benchbuild'
    SOURCE = [
        Git(remote='https://github.com/LLNL/LULESH/',
            local='lulesh.git',
            limit=5,
            refspec='HEAD')
    ]
    CONTAINER = container.Buildah().from_('debian:buster-slim')

    def compile(self):
        lulesh_repo = local.path(self.source_of('lulesh.git'))
        self.cflags += ["-DUSE_MPI=0"]

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


class LuleshOMP(Project):
    """ LULESH, OpenMP """

    NAME: str = 'lulesh-omp'
    DOMAIN: str = 'scientific'
    GROUP: str = 'benchbuild'
    SOURCE = [
        Git(remote='https://github.com/LLNL/LULESH/',
            local='lulesh.git',
            limit=5,
            refspec='HEAD')
    ]
    CONTAINER = container.Buildah().from_('debian:buster-slim')

    def compile(self):
        lulesh_repo = local.path(self.source_of('lulesh.git'))
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
