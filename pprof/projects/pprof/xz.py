#!/usr/bin/evn python
#

from pprof.project import ProjectFactory
from pprof.projects.pprof.group import PprofGroup

from os import path
from plumbum import local


class XZ(PprofGroup):
    """ XZ """

    testfiles = ["text.html", "chicken.jpg", "control", "input.source",
                 "liberty.jpg"]

    class Factory:
        def create(self, exp):
            return XZ(exp, "xz", "compression")

    ProjectFactory.addFactory("XZ", Factory())

    def prepare(self):
        super(XZ, self).prepare()
        from plumbum.cmd import cp
        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        cp(testfiles, self.builddir)

    src_dir = "xz-5.2.1"
    src_file = src_dir + ".tar.gz"
    src_uri = "http://tukaani.org/xz/" + src_file

    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import tar

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar('xfz', path.join(self.builddir, self.src_file))

    def run_tests(self, experiment):
        from pprof.project import wrap
        from pprof.utils.run import run

        xz_dir = path.join(self.builddir, self.src_dir)
        exp = wrap(path.join(xz_dir, "src", "xz", "xz"), experiment)

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
        from pprof.utils.compiler import lt_clang
        from pprof.utils.run import run

        xz_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags)
        with local.cwd(xz_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang)):
                run(configure["--enable-threads=no", "--with-gnu-ld=yes",
                              "--disable-shared",
                              "--disable-dependency-tracking",
                              "--disable-xzdec", "--disable-lzmadec",
                              "--disable-lzmainfo", "--disable-lzma-links",
                              "--disable-scripts", "--disable-doc"])

    def build(self):
        from plumbum.cmd import make
        from pprof.utils.compiler import lt_clang
        from pprof.utils.run import run

        xz_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags,
                             self.compiler_extension)
            with local.cwd(xz_dir):
                run(make["CC=" + str(clang), "clean", "all"])
