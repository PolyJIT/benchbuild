from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import cp, make, tar
from benchbuild.utils.compiler import cc
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


class XZ(Project):
    """ XZ """
    NAME = 'xz'
    DOMAIN = 'compression'
    GROUP = 'benchbuild'
    VERSION = '5.2.1'

    testfiles = [
        "text.html", "chicken.jpg", "control", "input.source", "liberty.jpg"
    ]

    src_dir = "xz-{0}".format(VERSION)
    SRC_FILE = src_dir + ".tar.gz"
    src_uri = "http://tukaani.org/xz/" + SRC_FILE

    def compile(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar('xfz', self.SRC_FILE)
        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        cp(testfiles, self.builddir)

        clang = cc(self)
        with local.cwd(self.src_dir):
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
        exp = wrap(path.join(self.src_dir, "src", "xz", "xz"), self)

        # Compress
        runner(exp["--compress", "-f", "-k", "-e", "-9", "text.html"])
        runner(exp["--compress", "-f", "-k", "-e", "-9", "chicken.jpg"])
        runner(exp["--compress", "-f", "-k", "-e", "-9", "control"])
        runner(exp["--compress", "-f", "-k", "-e", "-9", "input.source"])
        runner(exp["--compress", "-f", "-k", "-e", "-9", "liberty.jpg"])

        # Decompress
        runner(exp["--decompress", "-f", "-k", "text.html.xz"])
        runner(exp["--decompress", "-f", "-k", "chicken.jpg.xz"])
        runner(exp["--decompress", "-f", "-k", "control.xz"])
        runner(exp["--decompress", "-f", "-k", "input.source.xz"])
        runner(exp["--decompress", "-f", "-k", "liberty.jpg.xz"])
