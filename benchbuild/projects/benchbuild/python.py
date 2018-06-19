from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import make, tar
from benchbuild.utils.compiler import cc, cxx
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


class Python(Project):
    """ python benchmarks """

    NAME = 'python'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    VERSION = '3.4.3'

    src_dir = "Python-{0}".format(VERSION)
    SRC_FILE = src_dir + ".tar.xz"
    src_uri = "https://www.python.org/ftp/python/{0}/".format(VERSION) \
        + SRC_FILE

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar("xfJ", self.SRC_FILE)

    def configure(self):
        clang = cc(self)
        clang_cxx = cxx(self)

        with local.cwd(self.src_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                run(configure["--disable-shared", "--without-gcc"])

    def build(self):
        with local.cwd(self.src_dir):
            run(make)

    def run_tests(self, runner):
        wrap(path.join(self.src_dir, "python"), self)

        with local.cwd(self.src_dir):
            run(make["-i", "test"])
