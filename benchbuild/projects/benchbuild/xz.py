from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import cp, make, tar
from benchbuild.utils.compiler import cc
from benchbuild.utils.downloader import with_wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


@with_wget({'5.2.1': 'http://tukaani.org/xz/xz-5.2.1.tar.gz'})
class XZ(Project):
    """ XZ """
    NAME = 'xz'
    DOMAIN = 'compression'
    GROUP = 'benchbuild'
    VERSION = '5.2.1'
    SRC_FILE = 'xz.tar.gz'

    testfiles = [
        "text.html", "chicken.jpg", "control", "input.source", "liberty.jpg"
    ]

    def compile(self):
        self.download()

        tar('xfz', self.src_file)

        test_dir = local.path(self.testdir)
        testfiles = [test_dir / x for x in self.testfiles]
        cp(testfiles, self.builddir)

        unpack_dir = local.path('xz-{0}'.format(self.version))
        clang = cc(self)
        with local.cwd(unpack_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang)):
                run(configure["--enable-threads=no", "--with-gnu-ld=yes",
                              "--disable-shared",
                              "--disable-dependency-tracking",
                              "--disable-xzdec", "--disable-lzmadec",
                              "--disable-lzmainfo", "--disable-lzma-links",
                              "--disable-scripts", "--disable-doc"])

            run(make["CC=" + str(clang), "clean", "all"])

    def run_tests(self, runner):
        unpack_dir = local.path('xz-{0}'.format(self.version))
        xz = wrap(unpack_dir / "src" / "xz" / "xz", self)

        # Compress
        runner(xz["--compress", "-f", "-k", "-e", "-9", "text.html"])
        runner(xz["--compress", "-f", "-k", "-e", "-9", "chicken.jpg"])
        runner(xz["--compress", "-f", "-k", "-e", "-9", "control"])
        runner(xz["--compress", "-f", "-k", "-e", "-9", "input.source"])
        runner(xz["--compress", "-f", "-k", "-e", "-9", "liberty.jpg"])

        # Decompress
        runner(xz["--decompress", "-f", "-k", "text.html.xz"])
        runner(xz["--decompress", "-f", "-k", "chicken.jpg.xz"])
        runner(xz["--decompress", "-f", "-k", "control.xz"])
        runner(xz["--decompress", "-f", "-k", "input.source.xz"])
        runner(xz["--decompress", "-f", "-k", "liberty.jpg.xz"])
