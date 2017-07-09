from os import path
from benchbuild.utils.wrapping import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.cmd import make, mkdir, tar
from plumbum import local


class TCC(BenchBuildGroup):
    NAME = 'tcc'
    DOMAIN = 'compilation'
    VERSION = '0.9.26'

    src_dir = "tcc-{0}".format(VERSION)
    SRC_FILE = src_dir + ".tar.bz2"
    src_uri = "http://download-mirror.savannah.gnu.org/releases/tinycc/" + \
        SRC_FILE

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar("xjf", self.SRC_FILE)

    def configure(self):
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)

        with local.cwd(self.src_dir):
            mkdir("build")
            with local.cwd("build"):
                configure = local["../configure"]
                run(configure["--cc="+str(clang), "--with-libgcc"])

    def build(self):
        with local.cwd(self.src_dir):
            with local.cwd("build"):
                run(make)

    def run_tests(self, experiment, run):
        with local.cwd(self.src_dir):
            with local.cwd("build"):
                wrap("tcc", experiment)
                inc_path = path.abspath("..")
                run(make["TCCFLAGS=-B{}".format(inc_path), "test", "-i"])
