from os import path

from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap
from benchbuild.utils.cmd import tar, find, make
from plumbum import local


class LibreSSL(BenchBuildGroup):
    """ OpenSSL """

    NAME = 'libressl'
    DOMAIN = 'encryption'
    VERSION = '2.1.6'

    src_dir = "libressl-{0}".format(VERSION)
    SRC_FILE = src_dir + ".tar.gz"
    src_uri = "http://ftp.openbsd.org/pub/OpenBSD/LibreSSL/" + SRC_FILE

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar("xfz", self.SRC_FILE)

    def configure(self):
        self.cflags += ["-fPIC"]
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        configure = local[path.join(self.src_dir, "configure")]

        with local.cwd(self.src_dir):
            with local.env(CC=str(clang)):
                run(configure["--disable-asm", "--disable-shared",
                              "--enable-static",
                              "--disable-dependency-tracking",
                              "--with-pic=yes"])

    def build(self):
        with local.cwd(self.src_dir):
            run(make["check"])

    def run_tests(self, experiment, run):
        with local.cwd(path.join(self.src_dir, "tests", ".libs")):
            files = find(".", "-type", "f", "-executable")
            for wrap_f in files.split("\n"):
                if wrap_f:
                    wrap(wrap_f, experiment)
        with local.cwd(self.src_dir):
            run(make["V=1", "check"])
