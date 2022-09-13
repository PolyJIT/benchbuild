import logging

import benchbuild as bb
from benchbuild.command import Command, WorkloadSet, SourceRoot
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.source import HTTP
from benchbuild.utils import path
from benchbuild.utils.cmd import patch

LOG = logging.getLogger(__name__)


class Linpack(bb.Project):
    """ Linpack (C-Version) """

    NAME = 'linpack'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    SOURCE = [
        HTTP(
            remote={'5_88': 'http://www.netlib.org/benchmark/linpackc.new'},
            local='linpack.c'
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    WORKLOADS = {WorkloadSet(): [Command(SourceRoot(".") / "linpack")]}

    def compile(self) -> None:
        lp_patch = path.template_path("patches/linpack.patch")
        (patch["-p0"] < lp_patch)()

        self.ldflags += ["-lm"]
        clang = bb.compiler.cc(self)
        _clang = bb.watch(clang)
        _clang("-o", 'linpack', "linpack.c")
