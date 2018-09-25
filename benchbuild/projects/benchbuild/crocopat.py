from glob import glob
from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import cat, make, unzip
from benchbuild.utils.compiler import cxx
from benchbuild.utils.downloader import Wget, with_wget
from benchbuild.utils.wrapping import wrap


@with_wget({
    "2.1.4": "http://crocopat.googlecode.com/files/crocopat-2.1.4.zip"
})
class Crocopat(Project):
    """ crocopat benchmark """

    NAME = 'crocopat'
    DOMAIN = 'verification'
    GROUP = 'benchbuild'
    VERSION = '2.1.4'
    SRC_FILE = "crocopat.zip"

    def run_tests(self, runner):
        exp = wrap(self.run_f, self)

        programs = glob(path.join(self.testdir, "programs", "*.rml"))
        projects = glob(path.join(self.testdir, "projects", "*.rsf"))
        for program in programs:
            for project in projects:
                runner((cat[project] | exp[program]), None)

    def compile(self):
        self.download()
        unzip(self.src_file)
        unpack_dir = "crocopat-{0}".format(self.version)

        crocopat_dir = path.join(unpack_dir, "src")
        self.cflags += ["-I.", "-ansi"]
        self.ldflags += ["-L.", "-lrelbdd"]
        clang_cxx = cxx(self)

        with local.cwd(crocopat_dir):
            make("CXX=" + str(clang_cxx))
