import os
from glob import glob

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
        lammps_dir = os.path.join(self.builddir, self.src_file, "src")
        exp = wrap(os.path.join(lammps_dir, "lmp_serial"), self)

        examples_dir = os.path.join(self.builddir, self.src_file, "examples")
        tests = glob(os.path.join(examples_dir, "./*/in.*"))

        for test in tests:
            dirname = os.path.dirname(test)
            with local.cwd(dirname):
                cmd = (exp < test)
                runner(cmd, None)

    def compile(self):
        self.download()
        self.ldflags += ["-lgomp"]

        clang_cxx = cxx(self)
        with local.cwd(os.path.join(self.src_file, "src")):
            run(make["CC=" + str(clang_cxx), "LINK=" +
                     str(clang_cxx), "clean", "serial"])
