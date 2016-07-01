from benchbuild.project import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang_cxx
from benchbuild.utils.downloader import Git
from benchbuild.utils.run import run

from plumbum import local
from plumbum.cmd import cp, make

from os import path
from glob import glob


class Lammps(BenchBuildGroup):
    """ LAMMPS benchmark """

    NAME = 'lammps'
    DOMAIN = 'scientific'

    def prepare(self):
        super(Lammps, self).prepare()
        cp("-vr", self.testdir, "test")

    def run_tests(self, experiment):
        lammps_dir = path.join(self.builddir, self.src_dir, "src")
        exp = wrap(path.join(lammps_dir, "lmp_serial"), experiment)

        with local.cwd("test"):
            tests = glob(path.join(self.testdir, "in.*"))
            for test in tests:
                cmd = (exp < test)
                run(cmd, None)

    src_dir = "lammps.git"
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
