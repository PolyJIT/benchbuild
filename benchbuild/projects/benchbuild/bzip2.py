from plumbum import local

from benchbuild import project
from benchbuild.utils.cmd import cp, make
from benchbuild.utils import compiler, download, run, wrapping


@download.with_git("https://github.com/PolyJIT/bzip2", limit=1, refspec="HEAD")
class Bzip2(project.Project):
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

        clang = compiler.cc(self)
        with local.cwd(self.src_file):
            run.run(make["CFLAGS=-O3", "CC=" + str(clang), "clean", "bzip2"])

    def run_tests(self, runner):
        bzip2 = wrapping.wrap(local.path(self.src_file) / "bzip2", self)

        # Compress
        runner(bzip2["-f", "-z", "-k", "--best", "text.html"])
        runner(bzip2["-f", "-z", "-k", "--best", "chicken.jpg"])
        runner(bzip2["-f", "-z", "-k", "--best", "control"])
        runner(bzip2["-f", "-z", "-k", "--best", "input.source"])
        runner(bzip2["-f", "-z", "-k", "--best", "liberty.jpg"])

        # Decompress
        runner(bzip2["-f", "-k", "--decompress", "text.html.bz2"])
        runner(bzip2["-f", "-k", "--decompress", "chicken.jpg.bz2"])
        runner(bzip2["-f", "-k", "--decompress", "control.bz2"])
        runner(bzip2["-f", "-k", "--decompress", "input.source.bz2"])
        runner(bzip2["-f", "-k", "--decompress", "liberty.jpg.bz2"])
