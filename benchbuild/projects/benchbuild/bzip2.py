from plumbum import local

from benchbuild import project
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import cp, make


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
            make_ = run.watch(make)
            make_("CFLAGS=-O3", "CC=" + str(clang), "clean", "bzip2")

    def run_tests(self):
        bzip2 = wrapping.wrap(local.path(self.src_file) / "bzip2", self)
        _bzip2 = run.watch(bzip2)

        # Compress
        _bzip2("-f", "-z", "-k", "--best", "text.html")
        _bzip2("-f", "-z", "-k", "--best", "chicken.jpg")
        _bzip2("-f", "-z", "-k", "--best", "control")
        _bzip2("-f", "-z", "-k", "--best", "input.source")
        _bzip2("-f", "-z", "-k", "--best", "liberty.jpg")

        # Decompress
        _bzip2("-f", "-k", "--decompress", "text.html.bz2")
        _bzip2("-f", "-k", "--decompress", "chicken.jpg.bz2")
        _bzip2("-f", "-k", "--decompress", "control.bz2")
        _bzip2("-f", "-k", "--decompress", "input.source.bz2")
        _bzip2("-f", "-k", "--decompress", "liberty.jpg.bz2")
