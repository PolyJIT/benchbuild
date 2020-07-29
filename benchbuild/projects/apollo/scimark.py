import benchbuild as bb
from benchbuild.source import HTTP
from benchbuild.utils.cmd import make, unzip


class SciMark(bb.Project):
    """SciMark"""

    NAME = 'scimark'
    DOMAIN = 'scientific'
    GROUP = 'apollo'

    SOURCE = [
        HTTP(remote={'2.1c': 'http://math.nist.gov/scimark2/scimark2_1c.zip'},
             local='scimark.zip')
    ]

    def compile(self):
        scimark_source = bb.path(self.source_of('scimark.zip'))
        clang = bb.compiler.cc(self)
        _clang = bb.watch(clang)
        unzip(bb.cwd / scimark_source)
        make("CC=" + str(_clang), "scimark2")

    def run_tests(self):
        scimark2 = bb.wrap(bb.path('scimark2'), self)
        _scimark2 = bb.watch(scimark2)
        _scimark2()
