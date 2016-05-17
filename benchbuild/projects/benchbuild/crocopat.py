from benchbuild.projects.benchbuild.group import BenchBuildGroup
from os import path
from glob import glob
from plumbum import local
from plumbum.cmd import cat


class Crocopat(BenchBuildGroup):
    """ crocopat benchmark """

    NAME = 'crocopat'
    DOMAIN = 'verification'

    def run_tests(self, experiment):
        from benchbuild.project import wrap
        from benchbuild.utils.run import run

        exp = wrap(self.run_f, experiment)

        programs = glob(path.join(self.testdir, "programs", "*.rml"))
        projects = glob(path.join(self.testdir, "projects", "*.rsf"))
        for program in programs:
            for project in projects:
                run((cat[project] | exp[program]), None)

    src_dir = "crocopat-2.1.4"
    src_file = src_dir + ".zip"
    src_uri = "http://crocopat.googlecode.com/files/" + src_file

    def download(self):
        from benchbuild.utils.downloader import Wget
        from plumbum.cmd import unzip

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            unzip(path.join(self.builddir, self.src_file))

    def configure(self):
        pass

    def build(self):
        from plumbum.cmd import make
        from benchbuild.utils.compiler import lt_clang_cxx

        crocopat_dir = path.join(self.builddir, self.src_dir, "src")
        with local.cwd(crocopat_dir):
            cflags = self.cflags + ["-I.", "-ansi"]
            ldflags = self.ldflags + ["-L.", "-lrelbdd"]
            with local.cwd(self.builddir):
                clang_cxx = lt_clang_cxx(cflags, ldflags,
                                         self.compiler_extension)
            make("CXX=" + str(clang_cxx))
