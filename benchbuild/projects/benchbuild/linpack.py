import logging

from benchbuild.project import Project
from benchbuild.utils.cmd import cp, patch
from benchbuild.utils.compiler import lt_clang
from benchbuild.utils.downloader import Wget
from benchbuild.utils.path import template_path
from benchbuild.utils.run import run

LOG = logging.getLogger(__name__)


class Linpack(Project):
    """ Linpack (C-Version) """

    NAME = 'linpack'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SRC_FILE = 'linpackc.new'

    src_uri = "http://www.netlib.org/benchmark/linpackc.new"

    def download(self):
        lp_patch = template_path("../projects/patches/linpack.patch")
        Wget(self.src_uri, "linpackc.new")
        cp("-a", "linpackc.new", "linpack.c")

        (patch["-p0"] < lp_patch)()

    def configure(self):
        pass

    def build(self):
        cflags = self.cflags
        ldflags = self.ldflags + ["-lm"]

        clang = lt_clang(cflags, ldflags, self.compiler_extension)
        run(clang["-o", self.run_f, "linpack.c"])
