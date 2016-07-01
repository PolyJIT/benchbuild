from benchbuild.project import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang_cxx
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from plumbum import local
from plumbum.cmd import cat, unzip, make
from os import path
from glob import glob


class Crocopat(BenchBuildGroup):
    """ crocopat benchmark """

    NAME = 'crocopat'
    DOMAIN = 'verification'

    def run_tests(self, experiment):
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
        Wget(self.src_uri, self.src_file)
        unzip(self.src_file)

    def configure(self):
        pass

    def build(self):
        crocopat_dir = path.join(self.src_dir, "src")
        cflags = self.cflags + ["-I.", "-ansi"]
        ldflags = self.ldflags + ["-L.", "-lrelbdd"]
        clang_cxx = lt_clang_cxx(cflags, ldflags, self.compiler_extension)

        with local.cwd(crocopat_dir):
            make("CXX=" + str(clang_cxx))
