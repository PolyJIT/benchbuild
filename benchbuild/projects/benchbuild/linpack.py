import logging

import benchbuild as bb
from benchbuild.utils import download, path
from benchbuild.utils.cmd import patch

LOG = logging.getLogger(__name__)


@download.with_wget({"5_88": "http://www.netlib.org/benchmark/linpackc.new"})
class Linpack(bb.Project):
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
        clang = bb.compiler.cc(self)
        _clang = bb.watch(clang)
        _clang("-o", 'linpack', "linpack.c")

    def run_tests(self):
        linpack = bb.wrap('linpack', self)
        _linpack = bb.watch(linpack)
        _linpack()
