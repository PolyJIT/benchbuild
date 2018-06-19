from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import cp, make, tar
from benchbuild.utils.compiler import cc
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


class Bzip2(Project):
    """ Bzip2 """

    NAME = 'bzip2'
    DOMAIN = 'compression'
    GROUP = 'benchbuild'
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
        clang = cc(self)
        with local.cwd(self.src_dir):
            run(make["CFLAGS=-O3", "CC=" + str(clang), "clean", "bzip2"])

    def prepare(self):
        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        cp(testfiles, '.')

    def run_tests(self, runner):
        exp = wrap(path.join(self.src_dir, "bzip2"), self)

        # Compress
        runner(exp["-f", "-z", "-k", "--best", "text.html"])
        runner(exp["-f", "-z", "-k", "--best", "chicken.jpg"])
        runner(exp["-f", "-z", "-k", "--best", "control"])
        runner(exp["-f", "-z", "-k", "--best", "input.source"])
        runner(exp["-f", "-z", "-k", "--best", "liberty.jpg"])

        # Decompress
        runner(exp["-f", "-k", "--decompress", "text.html.bz2"])
        runner(exp["-f", "-k", "--decompress", "chicken.jpg.bz2"])
        runner(exp["-f", "-k", "--decompress", "control.bz2"])
        runner(exp["-f", "-k", "--decompress", "input.source.bz2"])
        runner(exp["-f", "-k", "--decompress", "liberty.jpg.bz2"])
