from plumbum import local

from benchbuild import project
from benchbuild.downloads import Git
from benchbuild.utils import compiler, run, wrapping
from benchbuild.utils.cmd import make


class Lammps(project.Project):
    """ LAMMPS benchmark """

    VERSION = 'HEAD'
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
        lammps_repo = local.path(self.source[0].local)
        src = lammps_repo / 'src'
        examples = lammps_repo / "examples"

        lmp_serial = wrapping.wrap(src / "lmp_serial", self)
        tests = examples // "*" // "in.*"

        for test in tests:
            dirname = test.dirname
            with local.cwd(dirname):
                lmp_serial = run.watch((lmp_serial < test))
                lmp_serial(retcode=None)

    def compile(self):
        lammps_repo = local.path(self.source[0].local)
        src = lammps_repo / 'src'

        self.ldflags += ["-lgomp"]
        clang_cxx = compiler.cxx(self)
        with local.cwd(src):
            make_ = run.watch(make)
            make_("CC=" + str(clang_cxx), "LINK=" + str(clang_cxx), "clean",
                  "serial")
