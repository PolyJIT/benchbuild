from plumbum import local

from benchbuild.environments import container
from benchbuild.project import Project
from benchbuild.source import HTTP
from benchbuild.utils import compiler, run, wrapping
from benchbuild.utils.cmd import make, unzip


class SciMark(Project):
    """SciMark"""

    NAME = 'scimark'
    DOMAIN = 'scientific'
    GROUP = 'apollo'

    SOURCE = [
        HTTP(remote={'2.1c': 'http://math.nist.gov/scimark2/scimark2_1c.zip'},
             local='scimark.zip')
    ]
    CONTAINER = container.Buildah().from_('debian:buster-slim')

    def compile(self):
        scimark_source = local.path(self.source_of('scimark.zip'))
        clang = compiler.cc(self)

        unzip(local.cwd / scimark_source)
        make("CC=" + str(clang), "scimark2")

    def run_tests(self):
        scimark2 = wrapping.wrap(local.path('scimark2'), self)
        scimark2 = run.watch(scimark2)
        scimark2()
