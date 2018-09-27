from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import cp, make
from benchbuild.utils.compiler import cc
from benchbuild.utils.downloader import with_git
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


@with_git("https://gitlab.com/bzip/bzip2", limit=1, refspec="HEAD")
class Bzip2(Project):
    """ Bzip2 """

    NAME = 'bzip2'
    DOMAIN = 'compression'
    GROUP = 'benchbuild'
    VERSION = 'HEAD'

    testfiles = [
        "text.html", "chicken.jpg", "control", "input.source", "liberty.jpg"
    ]
    SRC_FILE = "bzip2.git"

    def compile(self):
        self.download()

        testfiles = [local.path(self.testdir) / x for x in self.testfiles]
        cp(testfiles, '.')

        clang = cc(self)
        with local.cwd(self.src_file):
            run(make["CFLAGS=-O3", "CC=" + str(clang), "clean", "bzip2"])

    def run_tests(self, runner):
        exp = wrap(local.path(self.src_file) / "bzip2", self)

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
