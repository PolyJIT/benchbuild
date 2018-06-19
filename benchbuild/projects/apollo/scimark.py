from os import path

from benchbuild.project import Project
from benchbuild.utils.cmd import make, unzip
from benchbuild.utils.compiler import cc
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


class SciMark(Project):
    """SciMark"""

    NAME = 'scimark'
    DOMAIN = 'scientific'
    GROUP = 'apollo'
    VERSION = "2.1c"

    SRC_FILE = "scimark2_1c.zip"
    src_uri = "http://math.nist.gov/scimark2/{0}".format(SRC_FILE)

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        unzip(path.join('.', self.SRC_FILE))

    def configure(self):
        pass

    def build(self):
        clang = cc(self)
        run(make["CC=" + str(clang), "scimark2"])

    def prepare(self):
        pass

    def run_tests(self, runner):
        exp = wrap(path.join(self.builddir, "scimark2"), self)
        runner(exp)
