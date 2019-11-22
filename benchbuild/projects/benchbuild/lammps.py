from plumbum import local

from benchbuild import project
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import make


@download.with_git("https://github.com/lammps/lammps", limit=5)
class Lammps(project.Project):
    """ LAMMPS benchmark """

    NAME = 'lammps'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SRC_FILE = 'lammps.git'
    VERSION = 'HEAD'

    def run_tests(self):
        src_path = local.path(self.src_file)
        lammps_dir = src_path / "src"
        lmp_serial = wrapping.wrap(lammps_dir / "lmp_serial", self)

        examples_dir = src_path / "examples"
        tests = examples_dir // "*" // "in.*"

        for test in tests:
            dirname = test.dirname
            with local.cwd(dirname):
                lmp_serial = run.watch((lmp_serial < test))
                lmp_serial(retcode=None)

    def compile(self):
        self.download()
        self.ldflags += ["-lgomp"]

        clang_cxx = compiler.cxx(self)
        with local.cwd(local.path(self.src_file) / "src"):
            make_ = run.watch(make)
            make_("CC=" + str(clang_cxx), "LINK=" + str(clang_cxx), "clean",
                  "serial")
