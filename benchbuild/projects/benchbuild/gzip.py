from plumbum import local

from benchbuild import project
from benchbuild.settings import CFG
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import cp, make, tar


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

    def run_tests(self, runner):
        unpack_dir = local.path("gzip-{0}.tar.xz".format(self.version))
        gzip = wrapping.wrap(unpack_dir / "gzip", self)

        # Compress
        runner(gzip["-f", "-k", "--best", "text.html"])
        runner(gzip["-f", "-k", "--best", "chicken.jpg"])
        runner(gzip["-f", "-k", "--best", "control"])
        runner(gzip["-f", "-k", "--best", "input.source"])
        runner(gzip["-f", "-k", "--best", "liberty.jpg"])

        # Decompress
        runner(gzip["-f", "-k", "--decompress", "text.html.gz"])
        runner(gzip["-f", "-k", "--decompress", "chicken.jpg.gz"])
        runner(gzip["-f", "-k", "--decompress", "control.gz"])
        runner(gzip["-f", "-k", "--decompress", "input.source.gz"])
        runner(gzip["-f", "-k", "--decompress", "liberty.jpg.gz"])

    def compile(self):
        self.download()
        tar("xfJ", self.src_file)
        unpack_dir = "gzip-{0}.tar.xz".format(self.version)

        testfiles = [local.path(self.testdir) / x for x in self.testfiles]
        cp(testfiles, '.')

        clang = compiler.cc(self)
        with local.cwd(unpack_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang)):
                run.run(configure["--disable-dependency-tracking",
                                  "--disable-silent-rules", "--with-gnu-ld"])
            run.run(make["-j" + str(CFG["jobs"]), "clean", "all"])
