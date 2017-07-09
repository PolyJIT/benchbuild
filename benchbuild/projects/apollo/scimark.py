from os import path
from benchbuild.projects.apollo.group import ApolloGroup
from benchbuild.utils.wrapping import wrap
from benchbuild.utils.compiler import lt_clang
from benchbuild.utils.downloader import Wget
from benchbuild.utils.cmd import unzip, make
from benchbuild.utils.run import run


class SciMark(ApolloGroup):
    """SciMark"""

    NAME = 'scimark'
    DOMAIN = 'scientific'
    VERSION = "2.1c"

    SRC_FILE = "scimark2_1c.zip"
    src_uri = "http://math.nist.gov/scimark2/{0}".format(SRC_FILE)

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        unzip(path.join('.', self.SRC_FILE))

    def configure(self):
        pass

    def build(self):
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        run(make["CC=" + str(clang), "scimark2"])

    def prepare(self):
        pass

    def run_tests(self, experiment, run):
        exp = wrap(path.join(self.builddir, "scimark2"), experiment)
        run(exp)
