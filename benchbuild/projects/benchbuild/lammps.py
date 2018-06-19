import os
from glob import glob

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import make
from benchbuild.utils.compiler import cxx
from benchbuild.utils.downloader import Git
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


class Lammps(Project):
    """ LAMMPS benchmark """

    NAME = 'lammps'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SRC_FILE = 'lammps.git'

    def run_tests(self, runner):
        lammps_dir = os.path.join(self.builddir, self.src_dir, "src")
        exp = wrap(os.path.join(lammps_dir, "lmp_serial"), self)

        examples_dir = os.path.join(self.builddir, self.src_dir, "examples")
        tests = glob(os.path.join(examples_dir, "./*/in.*"))

        for test in tests:
            dirname = os.path.dirname(test)
            with local.cwd(dirname):
                cmd = (exp < test)
                runner(cmd, None)

    src_dir = SRC_FILE
    src_uri = "https://github.com/lammps/lammps"

    def download(self):
        Git(self.src_uri, self.src_dir)

    def configure(self):
        pass

    def build(self):
        self.ldflags += ["-lgomp"]

        clang_cxx = cxx(self)
        with local.cwd(os.path.join(self.src_dir, "src")):
            run(make["CC=" + str(clang_cxx),
                     "LINK=" + str(clang_cxx),
                     "clean", "serial"])
