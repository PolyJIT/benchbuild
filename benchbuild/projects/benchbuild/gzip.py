from plumbum import local

from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.cmd import cp, make, tar
from benchbuild.utils.compiler import cc
from benchbuild.utils.downloader import with_wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


@with_wget({"1.6": "http://ftpmirror.gnu.org/gzip/gzip-1.6.tar.xz"})
class Gzip(Project):
    """ Gzip """

    NAME = 'gzip'
    DOMAIN = 'compression'
    GROUP = 'benchbuild'
    VERSION = '1.6'
    SRC_FILE = "gzip.tar.xz"

    testfiles = [
        "text.html", "chicken.jpg", "control", "input.source", "liberty.jpg"
    ]

    def run_tests(self, runner):
        unpack_dir = local.path("gzip-{0}.tar.xz".format(self.version))
        exp = wrap(unpack_dir / "gzip", self)

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

    def compile(self):
        self.download()
        tar("xfJ", self.src_file)
        unpack_dir = "gzip-{0}.tar.xz".format(self.version)

        testfiles = [local.path(self.testdir) / x for x in self.testfiles]
        cp(testfiles, '.')

        clang = cc(self)
        with local.cwd(unpack_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang)):
                run(configure["--disable-dependency-tracking",
                              "--disable-silent-rules", "--with-gnu-ld"])
            run(make["-j" + str(CFG["jobs"].value()), "clean", "all"])
