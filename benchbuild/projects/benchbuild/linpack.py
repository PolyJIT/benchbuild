from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run

from plumbum.cmd import patch, cp

from os import path


class Linpack(BenchBuildGroup):
    """ Linpack (C-Version) """

    NAME = 'linpack'
    DOMAIN = 'scientific'

    src_uri = "http://www.netlib.org/benchmark/linpackc.new"

    def download(self):
        lp_patch = path.join(self.sourcedir, "linpack.patch")
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
