from os import path

from benchbuild.utils.wrapping import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.cmd import tar, cp, make
from plumbum import local


class XZ(BenchBuildGroup):
    """ XZ """
    NAME = 'xz'
    DOMAIN = 'compression'
    VERSION = '5.2.1'

    testfiles = ["text.html", "chicken.jpg", "control", "input.source",
                 "liberty.jpg"]

    def prepare(self):
        super(XZ, self).prepare()
        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        cp(testfiles, self.builddir)

    src_dir = "xz-{0}".format(VERSION)
    SRC_FILE = src_dir + ".tar.gz"
    src_uri = "http://tukaani.org/xz/" + SRC_FILE

    def download(self):
        Wget(self.src_uri, self.SRC_FILE)
        tar('xfz', self.SRC_FILE)

    def run_tests(self, experiment, run):
        exp = wrap(path.join(self.src_dir, "src", "xz", "xz"), experiment)

        # Compress
        run(exp["--compress", "-f", "-k", "-e", "-9", "text.html"])
        run(exp["--compress", "-f", "-k", "-e", "-9", "chicken.jpg"])
        run(exp["--compress", "-f", "-k", "-e", "-9", "control"])
        run(exp["--compress", "-f", "-k", "-e", "-9", "input.source"])
        run(exp["--compress", "-f", "-k", "-e", "-9", "liberty.jpg"])

        # Decompress
        run(exp["--decompress", "-f", "-k", "text.html.xz"])
        run(exp["--decompress", "-f", "-k", "chicken.jpg.xz"])
        run(exp["--decompress", "-f", "-k", "control.xz"])
        run(exp["--decompress", "-f", "-k", "input.source.xz"])
        run(exp["--decompress", "-f", "-k", "liberty.jpg.xz"])

    def configure(self):
        clang = lt_clang(self.cflags, self.ldflags)
        with local.cwd(self.src_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang)):
                run(configure["--enable-threads=no", "--with-gnu-ld=yes",
                              "--disable-shared",
                              "--disable-dependency-tracking",
                              "--disable-xzdec", "--disable-lzmadec",
                              "--disable-lzmainfo", "--disable-lzma-links",
                              "--disable-scripts", "--disable-doc"])

    def build(self):
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        with local.cwd(self.src_dir):
            run(make["CC=" + str(clang), "clean", "all"])
