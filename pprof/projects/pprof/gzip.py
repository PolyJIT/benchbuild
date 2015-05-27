#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

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
        for x in self.testfiles:
            self.products.add(path.join(self.builddir, x))
            self.products.add(path.join(self.builddir, x + ".gz"))

        super(Gzip, self).clean()

    def prepare(self):
        super(Gzip, self).prepare()
        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        cp[testfiles, self.builddir] & FG

    def run_tests(self, experiment):
        from pprof.project import wrap_tool
        gzip_dir = path.join(self.builddir, self.src_dir)
        exp = wrap_tool(path.join(gzip_dir, "gzip", experiment))

        # Compress
        exp["-f", "-k", "--best", "text.html"] & FG
        exp["-f", "-k", "--best", "chicken.jpg"] & FG
        exp["-f", "-k", "--best", "control"] & FG
        exp["-f", "-k", "--best", "input.source"] & FG
        exp["-f", "-k", "--best", "liberty.jpg"] & FG

        # Decompress
        exp["-f", "-k", "--decompress", "text.html.gz"] & FG
        exp["-f", "-k", "--decompress", "chicken.jpg.gz"] & FG
        exp["-f", "-k", "--decompress", "control.gz"] & FG
        exp["-f", "-k", "--decompress", "input.source.gz"] & FG
        exp["-f", "-k", "--decompress", "liberty.jpg.gz"] & FG

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
        from pprof.utils.compiler import clang
        gzip_dir = path.join(self.builddir, self.src_dir)

        with local.cwd(gzip_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang()),
                           CFLAGS=" ".join(self.cflags),
                           LDFLAGS=" ".join(self.ldflags),
                           LIBS=" ".join(self.ldflags)):
                configure("--disable-dependency-tracking",
                          "--disable-silent-rules",
                          "--with-gnu-ld")

    def build(self):
        from plumbum.cmd import make, ln
        from pprof.utils.compiler import clang, llvm_libs

        gzip_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(gzip_dir):
            with local.env(LD_LIBRARY_PATH=llvm_libs()):
                make["-j" + config["jobs"], "clean", "all"] & FG
        ln("-sf", path.join(gzip_dir, "gzip"), self.run_f)
