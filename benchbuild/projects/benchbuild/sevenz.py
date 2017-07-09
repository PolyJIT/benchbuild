from os import path

from benchbuild.utils.wrapping import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.cmd import make, tar, cp
from plumbum import local


class SevenZip(BenchBuildGroup):
    """ 7Zip """

    NAME = '7z'
    DOMAIN = 'compression'
    VERSION = '9.38.1'

    def run_tests(self, experiment, run):
        exp = wrap(path.join(self.src_dir, "bin", "7za"), experiment)
        run(exp["b", "-mmt1"])

    src_dir = "p7zip_{0}".format(VERSION)
    SRC_FILE = src_dir + "_src_all.tar.bz2"
    src_uri = "http://downloads.sourceforge.net/project/p7zip/p7zip/{0}/".format(VERSION) + \
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
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)

        with local.cwd(self.src_dir):
            run(make["CC=" + str(clang), "CXX=" + str(clang_cxx), "clean",
                     "all"])
