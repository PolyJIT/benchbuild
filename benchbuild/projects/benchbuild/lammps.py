from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import make
from benchbuild.utils.compiler import cxx
from benchbuild.utils.downloader import with_git
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


@with_git("https://github.com/lammps/lammps", limit=5)
class Lammps(Project):
    """ LAMMPS benchmark """

    NAME = 'lammps'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SRC_FILE = 'lammps.git'
    VERSION = 'HEAD'

    def run_tests(self, runner):
        src_path = local.path(self.src_file)
        lammps_dir = src_path / "src"
        exp = wrap(lammps_dir / "lmp_serial", self)

        examples_dir = src_path / "examples"
        tests = examples_dir // "*" // "in.*"

        for test in tests:
            dirname = test.dirname
            with local.cwd(dirname):
                cmd = (exp < test)
                runner(cmd, None)

    def compile(self):
        self.download()
        self.ldflags += ["-lgomp"]

        clang_cxx = cxx(self)
        with local.cwd(local.path(self.src_file) / "src"):
            run(make["CC=" + str(clang_cxx), "LINK=" +
                     str(clang_cxx), "clean", "serial"])
