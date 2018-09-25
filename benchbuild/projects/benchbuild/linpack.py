import logging

from benchbuild.project import Project
from benchbuild.utils.cmd import cp, patch
from benchbuild.utils.compiler import cc
from benchbuild.utils.downloader import Wget, with_wget
from benchbuild.utils.path import template_path
from benchbuild.utils.run import run

LOG = logging.getLogger(__name__)


@with_wget({"5/88": "http://www.netlib.org/benchmark/linpackc.new"})
class Linpack(Project):
    """ Linpack (C-Version) """

    NAME = 'linpack'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SRC_FILE = 'linpack.c'
    VERSION = '5/88'

    def compile(self):
        self.download()
        lp_patch = template_path("../projects/patches/linpack.patch")
        (patch["-p0"] < lp_patch)()

        self.ldflags += ["-lm"]
        clang = cc(self)
        run(clang["-o", self.run_f, "linpack.c"])
