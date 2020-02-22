import logging

from benchbuild.project import Project
from benchbuild.environments import container
from benchbuild.source import HTTP
from benchbuild.utils import path
from benchbuild.utils.cmd import patch

LOG = logging.getLogger(__name__)


class Linpack(Project):
    """ Linpack (C-Version) """

    NAME: str = 'linpack'
    DOMAIN: str = 'scientific'
    GROUP: str = 'benchbuild'
    SOURCE = [
        HTTP(remote={'5_88': 'http://www.netlib.org/benchmark/linpackc.new'},
             local='linpack.c')
    ]
    CONTAINER = container.Buildah().from_('debian:buster-slim')

    def compile(self):
        lp_patch = path.template_path("../projects/patches/linpack.patch")
        (patch["-p0"] < lp_patch)()

        self.ldflags += ["-lm"]
        clang = compiler.cc(self)
        clang = run.watch(clang)
        clang("-o", 'linpack', "linpack.c")

    def run_tests(self):
        linpack = wrapping.wrap('linpack', self)
        linpack = run.watch(linpack)
        linpack()
