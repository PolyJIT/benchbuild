import benchbuild as bb
from benchbuild.utils.cmd import make, unzip
from benchbuild.utils.download import with_wget


@with_wget({'2.1c': 'http://math.nist.gov/scimark2/scimark2_1c.zip'})
class SciMark(bb.Project):
    """SciMark"""

    NAME = 'scimark'
    DOMAIN = 'scientific'
    GROUP = 'apollo'
    VERSION = "2.1c"
    SRC_FILE = "scimark.zip"

    def compile(self):
        self.download()
        unzip(bb.cwd / self.src_file)
        clang = bb.compiler.cc(self)
        _clang = bb.watch(clang)
        make("CC=" + str(_clang), "scimark2")

    def run_tests(self):
        scimark2 = bb.wrap(bb.path('scimark2'), self)
        _scimark2 = bb.watch(scimark2)
        _scimark2()
