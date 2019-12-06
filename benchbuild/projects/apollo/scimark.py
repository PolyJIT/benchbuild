from plumbum import local

import benchbuild as bb

from benchbuild.downloads import HTTP
from benchbuild.utils.cmd import make, unzip


class SciMark(bb.Project):
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
        scimark_source = bb.path(self.source_of('scimark.zip'))
        clang = bb.compiler.cc(self)

        unzip(local.cwd / scimark_source)
        make("CC=" + str(clang), "scimark2")

    def run_tests(self):
        scimark2 = bb.wrap(bb.path('scimark2'), self)
        scimark2 = bb.watch(scimark2)
        scimark2()
