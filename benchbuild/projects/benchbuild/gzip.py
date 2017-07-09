from os import path

from benchbuild.utils.wrapping import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.settings import CFG
from benchbuild.utils.compiler import lt_clang
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.cmd import cp, make, tar

from plumbum import local


class Gzip(BenchBuildGroup):
    """ Gzip """

    NAME = 'gzip'
    DOMAIN = 'compression'
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

    def run_tests(self, experiment, run):
        exp = wrap(path.join(self.src_dir, "gzip"), experiment)

        # Compress
        run(exp["-f", "-k", "--best", "text.html"])
        run(exp["-f", "-k", "--best", "chicken.jpg"])
        run(exp["-f", "-k", "--best", "control"])
        run(exp["-f", "-k", "--best", "input.source"])
        run(exp["-f", "-k", "--best", "liberty.jpg"])

        # Decompress
        run(exp["-f", "-k", "--decompress", "text.html.gz"])
        run(exp["-f", "-k", "--decompress", "chicken.jpg.gz"])
        run(exp["-f", "-k", "--decompress", "control.gz"])
        run(exp["-f", "-k", "--decompress", "input.source.gz"])
        run(exp["-f", "-k", "--decompress", "liberty.jpg.gz"])

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar("xfJ", self.SRC_FILE)

    def configure(self):
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        with local.cwd(self.src_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang)):
                run(configure["--disable-dependency-tracking",
                              "--disable-silent-rules", "--with-gnu-ld"])

    def build(self):
        with local.cwd(self.src_dir):
            run(make["-j" + str(CFG["jobs"].value()), "clean", "all"])
