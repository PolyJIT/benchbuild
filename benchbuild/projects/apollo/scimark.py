from plumbum import local

from benchbuild.project import Project
from benchbuild.downloads import HTTP
from benchbuild.utils import compiler, run, wrapping
from benchbuild.utils.cmd import make, unzip


class SciMark(Project):
    """SciMark"""

    NAME = 'scimark'
    DOMAIN = 'scientific'
    GROUP = 'apollo'
    VERSION = "2.1c"

    SOURCE = [
        HTTP(remote={'2.1c': 'http://math.nist.gov/scimark2/scimark2_1c.zip'},
             local='scimark.zip')
    ]

    def compile(self):
        scimark_source = self.source[0]
        clang = compiler.cc(self)

        unzip(local.cwd / scimark_source.local)
        make("CC=" + str(clang), "scimark2")

    def run_tests(self):
        scimark2 = wrapping.wrap(local.path('scimark2'), self)
        scimark2 = run.watch(scimark2)
        scimark2()
