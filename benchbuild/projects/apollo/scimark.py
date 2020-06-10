from plumbum import local

from benchbuild.project import Project
from benchbuild.utils import run
from benchbuild.utils.cmd import make, unzip
from benchbuild.utils.compiler import cc
from benchbuild.utils.download import with_wget
from benchbuild.utils.wrapping import wrap


@with_wget({'2.1c': 'http://math.nist.gov/scimark2/scimark2_1c.zip'})
class SciMark(Project):
    """SciMark"""

    NAME = 'scimark'
    DOMAIN = 'scientific'
    GROUP = 'apollo'
    VERSION = "2.1c"
    SRC_FILE = "scimark.zip"

    def compile(self):
        self.download()
        unzip(local.cwd / self.src_file)
        clang = cc(self)
        _clang = run.watch(clang)
        make("CC=" + str(_clang), "scimark2")

    def run_tests(self):
        scimark2 = wrap(local.path('scimark2'), self)
        _scimark2 = run.watch(scimark2)
        _scimark2()
