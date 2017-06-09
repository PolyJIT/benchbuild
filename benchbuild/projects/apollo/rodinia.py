
from benchbuild.projects.apollo.group import ApolloGroup
from benchbuild.utils.wrapping import wrap
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.downloader import Wget
from benchbuild.utils.cmd import tar, make
from benchbuild.utils.run import run
from plumbum import local
from os import path

class Rodinia(ApolloGroup):
    """Rodinia"""

    NAME = 'rodinia'
    DOMAIN = 'scientific'
    VERSION = "3.1"

    src_dir = "rodinia_{0}".format(VERSION)
    SRC_FILE = "{0}.tar.bz2".format(src_dir)
    src_uri = ("http://www.cs.virginia.edu/~kw5na/lava/Rodinia/Packages/"
               "Current/{0}".format(SRC_FILE))

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar("xf", path.join('.', self.SRC_FILE))

    def configure(self):
        pass

    def build(self):
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)
        with local.cwd(self.src_dir):
            run(make["CC=" + str(clang), "CXX=" + str(clang_cxx), "OMP"])

    def prepare(self):
        pass

    def run_tests(self, experiment, run):
        import logging
        logging.error("================")
        logging.error("Not implemented.")
        logging.error("================")
