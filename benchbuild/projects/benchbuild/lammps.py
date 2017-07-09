from os import path
from glob import glob

from benchbuild.utils.wrapping import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang_cxx
from benchbuild.utils.downloader import Git
from benchbuild.utils.run import run
from benchbuild.utils.cmd import cp, make
from plumbum import local


class Lammps(BenchBuildGroup):
    """ LAMMPS benchmark """

    NAME = 'lammps'
    DOMAIN = 'scientific'
    SRC_FILE = 'lammps.git'

    def prepare(self):
        super(Lammps, self).prepare()
        cp("-vr", self.testdir, "test")

    def run_tests(self, experiment, run):
        lammps_dir = path.join(self.builddir, self.src_dir, "src")
        exp = wrap(path.join(lammps_dir, "lmp_serial"), experiment)

        with local.cwd("test"):
            tests = glob(path.join(self.testdir, "in.*"))
            for test in tests:
                cmd = (exp < test)
                run(cmd, None)

    src_dir = SRC_FILE
    src_uri = "https://github.com/lammps/lammps"

    def download(self):
        Git(self.src_uri, self.src_dir)

    def configure(self):
        pass

    def build(self):
        self.ldflags += ["-lgomp"]

        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)

        with local.cwd(path.join(self.src_dir, "src")):
            run(make[
                "CC=" + str(clang_cxx), "LINK=" + str(
                    clang_cxx), "clean", "serial"])
