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

    def run_tests(self, runner):
        src_path = local.path(self.src_file)
        lammps_dir = src_path / "src"
        exp = wrapping.wrap(lammps_dir / "lmp_serial", self)

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

        clang_cxx = compiler.cxx(self)
        with local.cwd(local.path(self.src_file) / "src"):
            run.run(make["CC=" + str(clang_cxx), "LINK=" +
                         str(clang_cxx), "clean", "serial"])
