from os import path

from benchbuild.utils.wrapping import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.cmd import make, tar, cp
from plumbum import local


class Bzip2(BenchBuildGroup):
    """ Bzip2 """

    NAME = 'bzip2'
    DOMAIN = 'compression'
    VERSION = '1.0.6'

    testfiles = ["text.html", "chicken.jpg", "control", "input.source",
                 "liberty.jpg"]
    src_dir = "bzip2-{0}".format(VERSION)
    SRC_FILE = src_dir + ".tar.gz"
    src_uri = "http://www.bzip.org/{0}/".format(VERSION) + SRC_FILE

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar('xfz', path.join('.', self.SRC_FILE))

    def configure(self):
        pass

    def build(self):
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        with local.cwd(self.src_dir):
            run(make["CFLAGS=-O3", "CC=" + str(clang), "clean", "bzip2"])

    def prepare(self):
        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        cp(testfiles, '.')

    def run_tests(self, experiment, run):
        exp = wrap(path.join(self.src_dir, "bzip2"), experiment)

        # Compress
        run(exp["-f", "-z", "-k", "--best", "text.html"])
        run(exp["-f", "-z", "-k", "--best", "chicken.jpg"])
        run(exp["-f", "-z", "-k", "--best", "control"])
        run(exp["-f", "-z", "-k", "--best", "input.source"])
        run(exp["-f", "-z", "-k", "--best", "liberty.jpg"])

        # Decompress
        run(exp["-f", "-k", "--decompress", "text.html.bz2"])
        run(exp["-f", "-k", "--decompress", "chicken.jpg.bz2"])
        run(exp["-f", "-k", "--decompress", "control.bz2"])
        run(exp["-f", "-k", "--decompress", "input.source.bz2"])
        run(exp["-f", "-k", "--decompress", "liberty.jpg.bz2"])
