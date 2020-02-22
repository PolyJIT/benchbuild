from benchbuild.project import Project
from benchbuild.environments import container
from benchbuild.source import Git
from benchbuild.utils.cmd import make


class Lammps(Project):
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
    CONTAINER = container.Buildah().from_('debian:buster-slim')

    def run_tests(self):
        lammps_repo = local.path(self.source_of('lammps.git'))
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
        lammps_repo = local.path(self.source_of('lammps.git'))
        src = lammps_repo / 'src'

        self.ldflags += ["-lgomp"]
        clang_cxx = compiler.cxx(self)
        with local.cwd(src):
            make_ = run.watch(make)
            make_("CC=" + str(clang_cxx), "LINK=" + str(clang_cxx), "clean",
                  "serial")
