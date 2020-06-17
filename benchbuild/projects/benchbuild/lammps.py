from benchbuild import project
from benchbuild.utils import download
from benchbuild.utils.cmd import make


@download.with_git("https://github.com/lammps/lammps", limit=5)
class Lammps(bb.Project):
    """ LAMMPS benchmark """

    NAME = 'lammps'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SRC_FILE = 'lammps.git'
    VERSION = 'HEAD'

    def run_tests(self):
        src_path = bb.path(self.src_file)
        lammps_dir = src_path / "src"
        lmp_serial = bb.wrap(lammps_dir / "lmp_serial", self)

        examples_dir = src_path / "examples"
        tests = examples_dir // "*" // "in.*"

        for test in tests:
            dirname = test.dirname
            with bb.cwd(dirname):
                _lmp_serial = bb.watch((lmp_serial < test))
                _lmp_serial(retcode=None)

    def compile(self):
        self.download()
        self.ldflags += ["-lgomp"]

        clang_cxx = bb.compiler.cxx(self)
        with bb.cwd(src):
            _make = bb.watch(make)
            _make("CC=" + str(clang_cxx), "LINK=" + str(clang_cxx), "clean",
                  "serial")
