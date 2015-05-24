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
            return Bzip2(exp, "bzip2", "compression")
    ProjectFactory.addFactory("Bzip2", Factory())

    @log_with(log)
    def clean(self):
        for x in self.testfiles:
            self.products.add(path.join(self.builddir, x))
            self.products.add(path.join(self.builddir, x + ".bz2"))

        super(Bzip2, self).clean()

    src_dir = "bzip2-1.0.6"
    src_file = src_dir + ".tar.gz"
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
        from pprof.utils.compiler import clang, llvm_libs

        bzip2_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(bzip2_dir):
            with local.env(LD_LIBRARY_PATH=llvm_libs()):
                make["CC=" + str(clang()),
                     "CFLAGS=" + " ".join(self.cflags),
                     "LDFLAGS=" + " ".join(self.ldflags), "clean", "bzip2"] & FG

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
        from pprof.project import wrap_tool

        exp = wrap_tool(path.join(self.src_dir, "bzip2"), experiment)

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
