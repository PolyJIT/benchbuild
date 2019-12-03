import logging

from benchbuild import project
from benchbuild.downloads import HTTP
from benchbuild.utils import compiler, path, run, wrapping
from benchbuild.utils.cmd import patch

LOG = logging.getLogger(__name__)


class Linpack(project.Project):
    """ Linpack (C-Version) """

    NAME = 'linpack'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    VERSION = '5_88'
    SOURCE = [
        HTTP(remote={'5_88': 'http://www.netlib.org/benchmark/linpackc.new'},
             local='linpack.c')
    ]

    def compile(self):
        lp_patch = path.template_path("../projects/patches/linpack.patch")
        (patch["-p0"] < lp_patch)()

        self.ldflags += ["-lm"]
        clang = compiler.cc(self)
        clang = run.watch(clang)
        clang("-o", 'linpack', "linpack.c")

    def run_tests(self):
        exp = wrapping.wrap('linpack', self)
        exp = run.watch(exp)
        exp()