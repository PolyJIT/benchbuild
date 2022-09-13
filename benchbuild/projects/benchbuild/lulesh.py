from plumbum import local

import benchbuild as bb
from benchbuild.command import WorkloadSet, Command, SourceRoot
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
    WORKLOADS = {
        WorkloadSet(): [
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 1),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 2),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 3),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 4),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 5),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 6),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 7),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 8),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 9),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 10),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 11),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 12),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 13),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 14),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 15)
        ]
    }

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
            clang(obj_files, "-lm", "-o", "lulesh")


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
    WORKLOADS = {
        WorkloadSet(): [
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 1),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 2),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 3),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 4),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 5),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 6),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 7),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 8),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 9),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 10),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 11),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 12),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 13),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 14),
            Command(SourceRoot("lulesh.git") / "lulesh", "-i", 15)
        ]
    }

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
            clang(obj_files, "-lm", "-o", "lulesh")
