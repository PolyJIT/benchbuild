#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import (ProjectFactory, log_with, log,
                           print_libtool_sucks_wrapper)
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
            obj = XZ(exp, "xz", "compression")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
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

    def run_tests(self, experiment):
        exp = experiment(self.run_f)
        # Compress
        exp["-f", "-k", "--compress", "-e", "-9", "text.html"] & FG
        exp["-f", "-k", "--compress", "-e", "-9", "chicken.jpg"] & FG
        exp["-f", "-k", "--compress", "-e", "-9", "control"] & FG
        exp[
            "-f",
            "-k",
            "--compress",
            "-e",
            "-9",
            "input.source"] & FG
        exp["-f", "-k", "--compress", "-e", "-9", "liberty.jpg"] & FG

        # Decompress
        exp["-f", "-k", "--decompress", "text.html.xz"] & FG
        exp["-f", "-k", "--decompress", "chicken.jpg.xz"] & FG
        exp["-f", "-k", "--decompress", "control.xz"] & FG
        exp["-f", "-k", "--decompress", "input.source.xz"] & FG
        exp["-f", "-k", "--decompress", "liberty.jpg.xz"] & FG


    
    src_file = "xz-5.2.1.tar.gz"
    src_uri = "http://tukaani.org/xz/" + src_file

    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import tar

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar('xfz', path.join(self.builddir, self.src_file))
        
    def configure(self):
        llvm = path.join(config["llvmdir"], "bin")
        llvm_libs = path.join(config["llvmdir"], "lib")
        ldflags = ["-L" + llvm_libs] + self.ldflags

        clang = local[path.join(llvm, "clang")]
        tar_f, _ = path.splitext(self.src_file)
        tar_x, _ = path.splitext(tar_f)
        configure = local[path.join(self.builddir, tar_x, "configure")]

        with local.cwd(path.join(self.builddir, tar_x)):
            with local.env(CC=str(clang),
                           LD_LIBRARY_PATH=llvm_libs):
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

        llvm = path.join(config["llvmdir"], "bin")
        llvm_libs = path.join(config["llvmdir"], "lib")

        clang = local[path.join(llvm, "clang")]
        tar_f, _ = path.splitext(self.src_file)
        tar_x, _ = path.splitext(tar_f)

        with local.cwd(self.builddir):
            print_libtool_sucks_wrapper("clang", self.cflags, str(clang))

        clang = local[path.join(self.builddir, "clang")]

        with local.cwd(path.join(self.builddir, tar_x)):
            with local.env(LD_LIBRARY_PATH=llvm_libs):
                make["CC=" + str(clang),
                     "LDFLAGS=" + " ".join(self.ldflags), "clean", "all"] & FG

        with local.cwd(self.builddir):
            ln("-sf", path.join(self.builddir, tar_x, "src", "xz", "xz"),
                      self.run_f)
