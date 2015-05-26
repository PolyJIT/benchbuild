#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local
from plumbum.cmd import cp


class XZ(PprofGroup):

    """ XZ """

    testfiles = ["text.html", "chicken.jpg", "control", "input.source",
                 "liberty.jpg"]

    class Factory:

        def create(self, exp):
            return XZ(exp, "xz", "compression")
    ProjectFactory.addFactory("XZ", Factory())

    def clean(self):
        for x in self.testfiles:
            self.products.add(path.join(self.builddir, x))
            self.products.add(path.join(self.builddir, x + ".xz"))

        super(XZ, self).clean()

    def prepare(self):
        super(XZ, self).prepare()
        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        cp[testfiles, self.builddir] & FG

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
        from pprof.project import wrap_tool

        xz_dir = path.join(self.builddir, self.src_dir)
        exp = wrap_tool(path.join(xz_dir, "src", "xz", "xz"), experiment)

        # Compress
        exp["-f", "-k", "--compress", "-e", "-9", "text.html"] & FG
        exp["-f", "-k", "--compress", "-e", "-9", "chicken.jpg"] & FG
        exp["-f", "-k", "--compress", "-e", "-9", "control"] & FG
        exp["-f", "-k", "--compress", "-e", "-9", "input.source"] & FG
        exp["-f", "-k", "--compress", "-e", "-9", "liberty.jpg"] & FG

        # Decompress
        exp["-f", "-k", "--decompress", "text.html.xz"] & FG
        exp["-f", "-k", "--decompress", "chicken.jpg.xz"] & FG
        exp["-f", "-k", "--decompress", "control.xz"] & FG
        exp["-f", "-k", "--decompress", "input.source.xz"] & FG
        exp["-f", "-k", "--decompress", "liberty.jpg.xz"] & FG

    def configure(self):
        from pprof.utils.compiler import lt_clang

        xz_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(xz_dir):
            configure = local["./configure"]
            with local.env(CC=str(lt_clang(self.cflags, self.ldflags)),
                           LD_LIBRARY_PATH=self.ldflags):
                configure["--enable-threads=no",
                          "--with-gnu-ld=yes",
                          "--disable-shared",
                          "--disable-dependency-tracking",
                          "--disable-xzdec",
                          "--disable-lzmadec",
                          "--disable-lzmainfo",
                          "--disable-lzma-links",
                          "--disable-scripts",
                          "--disable-doc"
                          ] & FG

    def build(self):
        from plumbum.cmd import make, ln
        from pprof.utils.compiler import lt_clang, llvm_libs

        xz_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(xz_dir):
            with local.env(LD_LIBRARY_PATH=llvm_libs()):
                make("CC=" + str(lt_clang(self.cflags, self.ldflags)),
                     "LDFLAGS=" + " ".join(self.ldflags), "clean", "all")
