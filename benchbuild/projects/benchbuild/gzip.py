from plumbum import local

from benchbuild import project
from benchbuild.settings import CFG
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import cp, make, tar
from benchbuild.utils.settings import get_number_of_jobs


@download.with_wget({"1.6": "http://ftpmirror.gnu.org/gzip/gzip-1.6.tar.xz"})
class Gzip(project.Project):
    """ Gzip """

    NAME = 'gzip'
    DOMAIN = 'compression'
    GROUP = 'benchbuild'
    VERSION = '1.6'
    SRC_FILE = "gzip.tar.xz"

    testfiles = [
        "text.html", "chicken.jpg", "control", "input.source", "liberty.jpg"
    ]

    def run_tests(self):
        unpack_dir = local.path("gzip-{0}.tar.xz".format(self.version))
        gzip = wrapping.wrap(unpack_dir / "gzip", self)
        _gzip = run.watch(gzip)

        # Compress
        _gzip("-f", "-k", "--best", "text.html")
        _gzip("-f", "-k", "--best", "chicken.jpg")
        _gzip("-f", "-k", "--best", "control")
        _gzip("-f", "-k", "--best", "input.source")
        _gzip("-f", "-k", "--best", "liberty.jpg")

        # Decompress
        _gzip("-f", "-k", "--decompress", "text.html.gz")
        _gzip("-f", "-k", "--decompress", "chicken.jpg.gz")
        _gzip("-f", "-k", "--decompress", "control.gz")
        _gzip("-f", "-k", "--decompress", "input.source.gz")
        _gzip("-f", "-k", "--decompress", "liberty.jpg.gz")

    def compile(self):
        self.download()
        tar("xfJ", self.src_file)
        unpack_dir = "gzip-{0}.tar.xz".format(self.version)

        testfiles = [local.path(self.testdir) / x for x in self.testfiles]
        cp(testfiles, '.')

        clang = compiler.cc(self)
        with local.cwd(unpack_dir):
            _configure = run.watch(local["./configure"])
            with local.env(CC=str(clang)):
                _configure("--disable-dependency-tracking",
                           "--disable-silent-rules", "--with-gnu-ld")
            _make = run.watch(make)
            _make("-j" + str(get_number_of_jobs(CFG)), "clean", "all")
