from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.cmd import cp, make, tar
from benchbuild.utils.compiler import cc
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


class Gzip(Project):
    """ Gzip """

    NAME = 'gzip'
    DOMAIN = 'compression'
    GROUP = 'benchbuild'
    VERSION = '1.6'

    testfiles = ["text.html", "chicken.jpg", "control", "input.source",
                 "liberty.jpg"]
    src_dir = "gzip-{0}".format(VERSION)
    SRC_FILE = src_dir + ".tar.xz"
    src_uri = "http://ftpmirror.gnu.org/gzip/" + SRC_FILE

    def prepare(self):
        super(Gzip, self).prepare()
        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        cp(testfiles, self.builddir)

    def run_tests(self, runner):
        exp = wrap(path.join(self.src_dir, "gzip"), self)

        # Compress
        runner(exp["-f", "-k", "--best", "text.html"])
        runner(exp["-f", "-k", "--best", "chicken.jpg"])
        runner(exp["-f", "-k", "--best", "control"])
        runner(exp["-f", "-k", "--best", "input.source"])
        runner(exp["-f", "-k", "--best", "liberty.jpg"])

        # Decompress
        runner(exp["-f", "-k", "--decompress", "text.html.gz"])
        runner(exp["-f", "-k", "--decompress", "chicken.jpg.gz"])
        runner(exp["-f", "-k", "--decompress", "control.gz"])
        runner(exp["-f", "-k", "--decompress", "input.source.gz"])
        runner(exp["-f", "-k", "--decompress", "liberty.jpg.gz"])

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar("xfJ", self.SRC_FILE)

    def configure(self):
        clang = cc(self)
        with local.cwd(self.src_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang)):
                run(configure["--disable-dependency-tracking",
                              "--disable-silent-rules", "--with-gnu-ld"])

    def build(self):
        with local.cwd(self.src_dir):
            run(make["-j" + str(CFG["jobs"].value()), "clean", "all"])
