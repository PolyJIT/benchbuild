#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local
from plumbum.cmd import cp


class Bzip2(PprofGroup):

    """ Bzip2 """

    testfiles = ["text.html", "chicken.jpg", "control", "input.source",
                 "liberty.jpg"]

    class Factory:
        def create(self, exp):
            obj = Bzip2(exp, "bzip2", "compression")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")

            return obj
    ProjectFactory.addFactory("Bzip2", Factory())

    @log_with(log)
    def clean(self):
        for x in self.testfiles:
            self.products.add(path.join(self.builddir, x))
            self.products.add(path.join(self.builddir, x + ".bz2"))

        super(Bzip2, self).clean()

    src_file = "bzip2-1.0.6.tar.gz"
    src_uri = "http://www.bzip.org/1.0.6/" + src_file

    @log_with(log)
    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import tar

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar('xfz', path.join(self.builddir, self.src_file))

    @log_with(log)
    def configure(self):
        pass

    @log_with(log)
    def build(self):
        from plumbum.cmd import make, ln
        from pprof.settings import config

        llvm = path.join(config["llvmdir"], "bin")
        llvm_libs = path.join(config["llvmdir"], "lib")

        clang = local[path.join(llvm, "clang")]
        tar_f, _ = path.splitext(self.src_file)
        tar_x, _ = path.splitext(tar_f)

        with local.cwd(path.join(self.builddir, tar_x)):
            with local.env(LD_LIBRARY_PATH=llvm_libs):
                make["CC=" + str(clang),
                     "CFLAGS=" + " ".join(self.cflags),
                     "LDFLAGS=" + " ".join(self.ldflags), "clean", "bzip2"] & FG

        with local.cwd(self.builddir):
            ln("-sf", path.join(self.builddir, tar_x, "bzip2"), self.run_f)

    @log_with(log)
    def pull_in_testfiles(self):
        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        cp[testfiles, self.builddir] & FG

    @log_with(log)
    def prepare(self):
        super(Bzip2, self).prepare()
        self.pull_in_testfiles()

    @log_with(log)
    def run_tests(self, experiment):
        exp = experiment(self.run_f)

        # Compress
        exp["-f", "-z", "-k", "--best", "text.html"] & FG
        exp["-f", "-z", "-k", "--best", "chicken.jpg"] & FG
        exp["-f", "-z", "-k", "--best", "control"] & FG
        exp["-f", "-z", "-k", "--best", "input.source"] & FG
        exp["-f", "-z", "-k", "--best", "liberty.jpg"] & FG

        # Decompress
        exp["-f", "-k", "--decompress", "text.html.bz2"] & FG
        exp["-f", "-k", "--decompress", "chicken.jpg.bz2"] & FG
        exp["-f", "-k", "--decompress", "control.bz2"] & FG
        exp["-f", "-k", "--decompress", "input.source.bz2"] & FG
        exp["-f", "-k", "--decompress", "liberty.jpg.bz2"] & FG
