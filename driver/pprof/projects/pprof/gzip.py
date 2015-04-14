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
            obj = Gzip(exp, "gzip", "compression")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
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

    def run(self, experiment):
        with local.cwd(self.builddir):
            # Compress
            experiment["-f", "--best", "text.html"] & FG
            experiment["-f", "--best", "chicken.jpg"] & FG
            experiment["-f", "--best", "control"] & FG
            experiment["-f", "--best", "input.source"] & FG
            experiment["-f", "--best", "liberty.jpg"] & FG

            # Decompress
            experiment["-f", "--decompress", "text.html.gz"] & FG
            experiment["-f", "--decompress", "chicken.jpg.gz"] & FG
            experiment["-f", "--decompress", "control.gz"] & FG
            experiment["-f", "--decompress", "input.source.gz"] & FG
            experiment["-f", "--decompress", "liberty.jpg.gz"] & FG

    src_file = "gzip-1.2.4.tar"
    src_uri = "http://ftpmirror.gnu.org/gzip/" + src_file
    def download(self):
        from plumbum.cmd import wget, tar

        with local.cwd(self.builddir):
            wget(self.src_uri)
            tar("xf", path.join(self.builddir, self.src_file))

    def configure(self):
        tar_x, _ = path.splitext(self.src_file)
        configure = local[path.join(self.builddir, tar_x, "configure")]

        with local.cwd(path.join(self.builddir, tar_x)):
            configure & FG

    def build(self):
        from plumbum.cmd import make, ln

        llvm = path.join(config["llvmdir"], "bin")
        llvm_libs = path.join(config["llvmdir"], "lib")

        clang = local[path.join(llvm, "clang")]
        tar_x, _ = path.splitext(self.src_file)
        gzip_dir = path.join(self.builddir, tar_x)

        with local.cwd(gzip_dir):
            with local.env(LD_LIBRARY_PATH=llvm_libs):
                make["CC=" + str(clang),
                     "CFLAGS=" + " ".join(self.cflags),
                     "LDFLAGS=" + " ".join(self.ldflags), "clean", "all"] & FG

            ln("-sf", path.join(gzip_dir, "gzip"), self.run_f)
