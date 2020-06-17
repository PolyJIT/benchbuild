import benchbuild as bb
from benchbuild import project
from benchbuild.utils import download
from benchbuild.utils.cmd import cp, make


@download.with_git("https://github.com/PolyJIT/bzip2", limit=1, refspec="HEAD")
class Bzip2(bb.Project):
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

        testfiles = [bb.path(self.testdir) / x for x in self.testfiles]
        cp(testfiles, '.')

        clang = bb.compiler.cc(self)
        with bb.cwd(self.src_file):
            make_ = bb.watch(make)
            make_("CFLAGS=-O3", "CC=" + str(clang), "clean", "bzip2")

    def run_tests(self):
        bzip2 = bb.wrap(bb.path(self.src_file) / "bzip2", self)
        _bzip2 = bb.watch(bzip2)

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
