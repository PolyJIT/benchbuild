from plumbum import local

import benchbuild as bb
from benchbuild.command import Command, WorkloadSet, SourceRoot
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.source import HTTP
from benchbuild.utils.cmd import make, unzip


class SciMark(bb.Project):
    """SciMark"""

    NAME = 'scimark'
    DOMAIN = 'scientific'
    GROUP = 'apollo'

    SOURCE = [
        HTTP(
            remote={'2.1c': 'http://math.nist.gov/scimark2/scimark2_1c.zip'},
            local='scimark.zip'
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    WORKLOADS = {WorkloadSet(): [Command(SourceRoot(".") / "scimark2")]}

    def compile(self):
        scimark_source = local.path(self.source_of('scimark.zip'))
        clang = bb.compiler.cc(self)
        _clang = bb.watch(clang)
        unzip(local.cwd / scimark_source)
        make("CC=" + str(_clang), "scimark2")
