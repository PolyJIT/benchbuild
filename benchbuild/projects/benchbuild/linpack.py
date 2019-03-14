import logging

from benchbuild import project
from benchbuild.utils import compiler, download, path, run
from benchbuild.utils.cmd import patch

LOG = logging.getLogger(__name__)


@download.with_wget({"5_88": "http://www.netlib.org/benchmark/linpackc.new"})
class Linpack(project.Project):
    """ Linpack (C-Version) """

    NAME = 'linpack'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SRC_FILE = 'linpack.c'
    VERSION = '5_88'

    def compile(self):
        self.download()
        lp_patch = path.template_path("../projects/patches/linpack.patch")
        (patch["-p0"] < lp_patch)()

        self.ldflags += ["-lm"]
        clang = compiler.cc(self)
        run.run(clang["-o", self.run_f, "linpack.c"])
