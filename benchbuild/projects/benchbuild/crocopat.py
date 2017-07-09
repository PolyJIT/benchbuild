from os import path
from glob import glob

from benchbuild.utils.wrapping import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang_cxx
from benchbuild.utils.downloader import Wget
from plumbum import local
from benchbuild.utils.cmd import cat, unzip, make


class Crocopat(BenchBuildGroup):
    """ crocopat benchmark """

    NAME = 'crocopat'
    DOMAIN = 'verification'
    VERSION = '2.1.4'

    def run_tests(self, experiment, run):
        exp = wrap(self.run_f, experiment)

        programs = glob(path.join(self.testdir, "programs", "*.rml"))
        projects = glob(path.join(self.testdir, "projects", "*.rsf"))
        for program in programs:
            for project in projects:
                run((cat[project] | exp[program]), None)

    src_dir = "crocopat-{0}".format(VERSION)
    SRC_FILE = src_dir + ".zip"
    src_uri = "http://crocopat.googlecode.com/files/" + SRC_FILE

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        unzip(self.SRC_FILE)

    def configure(self):
        pass

    def build(self):
        crocopat_dir = path.join(self.src_dir, "src")
        cflags = self.cflags + ["-I.", "-ansi"]
        ldflags = self.ldflags + ["-L.", "-lrelbdd"]
        clang_cxx = lt_clang_cxx(cflags, ldflags, self.compiler_extension)

        with local.cwd(crocopat_dir):
            make("CXX=" + str(clang_cxx))
