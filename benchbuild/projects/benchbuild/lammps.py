from benchbuild.projects.benchbuild.group import BenchBuildGroup
from os import path
from glob import glob
from plumbum import local


class Lammps(BenchBuildGroup):
    """ LAMMPS benchmark """

    NAME = 'lammps'
    DOMAIN = 'scientific'

    def prepare(self):
        super(Lammps, self).prepare()
        from plumbum.cmd import cp

        with local.cwd(self.builddir):
            cp("-vr", self.testdir, "test")

    def run_tests(self, experiment):
        from benchbuild.project import wrap
        from benchbuild.utils.run import run

        lammps_dir = path.join(self.builddir, self.src_dir, "src")
        exp = wrap(path.join(lammps_dir, "lmp_serial"), experiment)

        with local.cwd(path.join(self.builddir, "test")):
            tests = glob(path.join(self.testdir, "in.*"))
            for test in tests:
                cmd = (exp < test)
                run(cmd, None)

    src_dir = "lammps.git"
    src_uri = "https://github.com/lammps/lammps"

    def download(self):
        from benchbuild.utils.downloader import Git

        with local.cwd(self.builddir):
            Git(self.src_uri, self.src_dir)

    def configure(self):
        pass

    def build(self):
        from plumbum.cmd import make
        from benchbuild.utils.compiler import lt_clang_cxx
        from benchbuild.utils.run import run

        self.ldflags += ["-lgomp"]

        with local.cwd(self.builddir):
            clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                     self.compiler_extension)

        with local.cwd(path.join(self.builddir, self.src_dir, "src")):
            run(make[
                "CC=" + str(clang_cxx), "LINK=" + str(
                    clang_cxx), "clean", "serial"])
