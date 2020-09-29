from plumbum import local

import benchbuild as bb
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.source import Git
from benchbuild.utils.cmd import make


class Lammps(bb.Project):
    """ LAMMPS benchmark """

    NAME = 'lammps'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SOURCE = [
        Git(
            remote='https://github.com/lammps/lammps',
            local='lammps.git',
            limit=5,
            refspec='HEAD'
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def run_tests(self):
        lammps_repo = local.path(self.source_of('lammps.git'))
        src = lammps_repo / 'src'
        examples = lammps_repo / "examples"

        lmp_serial = bb.wrap(src / "lmp_serial", self)
        tests = examples // "*" // "in.*"

        for test in tests:
            dirname = test.dirname
            with local.cwd(dirname):
                _lmp_serial = bb.watch((lmp_serial < test))
                _lmp_serial(retcode=None)

    def compile(self):
        lammps_repo = local.path(self.source_of('lammps.git'))
        src = lammps_repo / 'src'

        self.ldflags += ["-lgomp"]
        clang_cxx = bb.compiler.cxx(self)
        with local.cwd(src):
            _make = bb.watch(make)
            _make(
                "CC=" + str(clang_cxx), "LINK=" + str(clang_cxx), "clean",
                "serial"
            )
