#!/usr/bin/evn python
# encoding: utf-8

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

    def clean(self):
        for test_f in self.testfiles:
            self.products.add(path.join(self.builddir, test_f))
            self.products.add(path.join(self.builddir, test_f + ".xz"))

        super(XZ, self).clean()

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

        xz_dir = path.join(self.builddir, self.src_dir)
        exp = wrap(path.join(xz_dir, "src", "xz", "xz"), experiment)

        # Compress
        exp("--compress", "-f", "-k", "-e", "-9", "text.html")
        exp("--compress", "-f", "-k", "-e", "-9", "chicken.jpg")
        exp("--compress", "-f", "-k", "-e", "-9", "control")
        exp("--compress", "-f", "-k", "-e", "-9", "input.source")
        exp("--compress", "-f", "-k", "-e", "-9", "liberty.jpg")

        # Decompress
        exp("--decompress", "-f", "-k", "text.html.xz")
        exp("--decompress", "-f", "-k", "chicken.jpg.xz")
        exp("--decompress", "-f", "-k", "control.xz")
        exp("--decompress", "-f", "-k", "input.source.xz")
        exp("--decompress", "-f", "-k", "liberty.jpg.xz")

    def configure(self):
        from pprof.utils.compiler import lt_clang

        xz_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags)
        with local.cwd(xz_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang)):
                configure("--enable-threads=no",
                          "--with-gnu-ld=yes",
                          "--disable-shared",
                          "--disable-dependency-tracking",
                          "--disable-xzdec",
                          "--disable-lzmadec",
                          "--disable-lzmainfo",
                          "--disable-lzma-links",
                          "--disable-scripts",
                          "--disable-doc")

    def build(self):
        from plumbum.cmd import make
        from pprof.utils.compiler import lt_clang

        xz_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags)
            with local.cwd(xz_dir):
                make("CC=" + str(clang()), "clean", "all")
