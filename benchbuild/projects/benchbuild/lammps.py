from plumbum import local

import benchbuild as bb

from benchbuild.downloads import Git
from benchbuild.utils.cmd import make


class Lammps(bb.Project):
    """ LAMMPS benchmark """

    NAME: str = 'lammps'
    DOMAIN: str = 'scientific'
    GROUP: str = 'benchbuild'
    SOURCE = [
        Git(remote='https://github.com/lammps/lammps',
            local='lammps.git',
            limit=5,
            refspec='HEAD')
    ]

    def run_tests(self):
        lammps_repo = bb.path(self.source_of('lammps.git'))
        src = lammps_repo / 'src'
        examples = lammps_repo / "examples"

        lmp_serial = bb.wrap(src / "lmp_serial", self)
        tests = examples // "*" // "in.*"

        for test in tests:
            dirname = test.dirname
            with bb.cwd(dirname):
                lmp_serial = bb.watch((lmp_serial < test))
                lmp_serial(retcode=None)

    def compile(self):
        lammps_repo = bb.path(self.source_of('lammps.git'))
        src = lammps_repo / 'src'

        self.ldflags += ["-lgomp"]
        clang_cxx = bb.compiler.cxx(self)
        with bb.cwd(src):
            make_ = bb.watch(make)
            make_("CC=" + str(clang_cxx), "LINK=" + str(clang_cxx), "clean",
                  "serial")
