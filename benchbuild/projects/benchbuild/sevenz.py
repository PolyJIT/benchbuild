from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import cp, make, tar
from benchbuild.utils.compiler import cc, cxx
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


class SevenZip(Project):
    """ 7Zip """

    NAME = '7z'
    DOMAIN = 'compression'
    GROUP = 'benchbuild'
    VERSION = '16.02'

    def run_tests(self, runner):
        exp = wrap(path.join(self.src_dir, "bin", "7za"), self)
        runner(exp["b", "-mmt1"])

    src_dir = "p7zip_{0}".format(VERSION)
    SRC_FILE = src_dir + "_src_all.tar.bz2"
    src_uri = "http://downloads.sourceforge.net/" \
              "project/p7zip/p7zip/{0}/".format(VERSION) + \
              SRC_FILE

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar('xfj', self.SRC_FILE)
        cp(
            path.join(self.src_dir, "makefile.linux_clang_amd64_asm"),
            path.join(self.src_dir, "makefile.machine"))

    def configure(self):
        pass

    def build(self):
        clang = cc(self)
        clang_cxx = cxx(self)

        with local.cwd(self.src_dir):
            run(make["CC=" + str(clang), "CXX=" + str(clang_cxx), "clean",
                     "all"])
