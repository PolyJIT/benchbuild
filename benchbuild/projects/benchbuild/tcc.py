from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import make, mkdir, tar
from benchbuild.utils.compiler import cc
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


class TCC(Project):
    NAME = 'tcc'
    DOMAIN = 'compilation'
    GROUP = 'benchbuild'
    VERSION = '0.9.26'

    src_dir = "tcc-{0}".format(VERSION)
    SRC_FILE = src_dir + ".tar.bz2"
    src_uri = "http://download-mirror.savannah.gnu.org/releases/tinycc/" + \
        SRC_FILE

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar("xjf", self.SRC_FILE)

    def configure(self):
        clang = cc(self)

        with local.cwd(self.src_dir):
            mkdir("build")
            with local.cwd("build"):
                configure = local["../configure"]
                run(configure["--cc="+str(clang), "--with-libgcc"])

    def build(self):
        with local.cwd(self.src_dir):
            with local.cwd("build"):
                run(make)

    def run_tests(self, runner):
        with local.cwd(self.src_dir):
            with local.cwd("build"):
                wrap("tcc", self)
                inc_path = path.abspath("..")
                run(make["TCCFLAGS=-B{}".format(inc_path), "test", "-i"])
