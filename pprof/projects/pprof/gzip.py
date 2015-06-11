#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory
from pprof.settings import config
from pprof.projects.pprof.group import PprofGroup

from os import path
from plumbum import FG, local
from plumbum.cmd import cp


class Gzip(PprofGroup):

    """ Gzip """

    testfiles = ["text.html", "chicken.jpg", "control", "input.source",
                 "liberty.jpg"]

    class Factory:

        def create(self, exp):
            return Gzip(exp, "gzip", "compression")
    ProjectFactory.addFactory("Gzip", Factory())

    def clean(self):
        for test_f in self.testfiles:
            self.products.add(path.join(self.builddir, test_f))
            self.products.add(path.join(self.builddir, test_f + ".gz"))

        super(Gzip, self).clean()

    def prepare(self):
        super(Gzip, self).prepare()
        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        cp(testfiles, self.builddir)

    def run_tests(self, experiment):
        from pprof.project import wrap
        gzip_dir = path.join(self.builddir, self.src_dir)
        exp = wrap(path.join(gzip_dir, "gzip"), experiment)

        # Compress
        exp("-f", "-k", "--best", "text.html")
        exp("-f", "-k", "--best", "chicken.jpg")
        exp("-f", "-k", "--best", "control")
        exp("-f", "-k", "--best", "input.source")
        exp("-f", "-k", "--best", "liberty.jpg")

        # Decompress
        exp("-f", "-k", "--decompress", "text.html.gz")
        exp("-f", "-k", "--decompress", "chicken.jpg.gz")
        exp("-f", "-k", "--decompress", "control.gz")
        exp("-f", "-k", "--decompress", "input.source.gz")
        exp("-f", "-k", "--decompress", "liberty.jpg.gz")

    src_dir = "gzip-1.6"
    src_file = src_dir + ".tar.xz"
    src_uri = "http://ftpmirror.gnu.org/gzip/" + src_file

    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import tar

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar("xfJ", path.join(self.builddir, self.src_file))

    def configure(self):
        from pprof.utils.compiler import lt_clang
        gzip_dir = path.join(self.builddir, self.src_dir)

        with local.cwd(gzip_dir):
            with local.cwd(self.builddir):
                clang = lt_clang(self.cflags, self.ldflags)
            configure = local["./configure"]
            with local.env(CC=str(clang)):
                configure("--disable-dependency-tracking",
                          "--disable-silent-rules",
                          "--with-gnu-ld")

    def build(self):
        from plumbum.cmd import make
        gzip_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(gzip_dir):
            make("-j" + config["jobs"], "clean", "all")
