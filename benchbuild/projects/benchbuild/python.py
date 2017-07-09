from os import path

from benchbuild.utils.wrapping import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.cmd import make, tar
from plumbum import local


class Python(BenchBuildGroup):
    """ python benchmarks """

    NAME = 'python'
    DOMAIN = 'compilation'
    VERSION = '3.4.3'

    src_dir = "Python-{0}".format(VERSION)
    SRC_FILE = src_dir + ".tar.xz"
    src_uri = "https://www.python.org/ftp/python/{0}/".format(VERSION) \
        + SRC_FILE

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar("xfJ", self.SRC_FILE)

    def configure(self):
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)

        with local.cwd(self.src_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                run(configure["--disable-shared", "--without-gcc"])

    def build(self):
        with local.cwd(self.src_dir):
            run(make)

    def run_tests(self, experiment, run):
        wrap(path.join(self.src_dir, "python"), experiment)

        with local.cwd(self.src_dir):
            run(make["-i", "test"])
