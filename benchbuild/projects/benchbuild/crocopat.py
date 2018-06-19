from glob import glob
from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import cat, make, unzip
from benchbuild.utils.compiler import cxx
from benchbuild.utils.downloader import Wget
from benchbuild.utils.wrapping import wrap


class Crocopat(Project):
    """ crocopat benchmark """

    NAME = 'crocopat'
    DOMAIN = 'verification'
    GROUP = 'benchbuild'
    VERSION = '2.1.4'

    def run_tests(self, runner):
        exp = wrap(self.run_f, self)

        programs = glob(path.join(self.testdir, "programs", "*.rml"))
        projects = glob(path.join(self.testdir, "projects", "*.rsf"))
        for program in programs:
            for project in projects:
                runner((cat[project] | exp[program]), None)

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
        self.cflags += ["-I.", "-ansi"]
        self.ldflags += ["-L.", "-lrelbdd"]
        clang_cxx = cxx(self)

        with local.cwd(crocopat_dir):
            make("CXX=" + str(clang_cxx))
