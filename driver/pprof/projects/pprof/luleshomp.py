#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local

class LuleshOMP(PprofGroup):

    """ Lulesh-OMP """

    class Factory:
        def create(self, exp):
            return LuleshOMP(exp, "lulesh-omp", "scientific")
    ProjectFactory.addFactory("LuleshOMP", Factory())

    def run_tests(self, experiment):
        experiment["20"] & FG

    src_file = "LULESH_OMP.cc"
    src_uri = "https://codesign.llnl.gov/lulesh/" + src_file
    def download(self):
        from pprof.utils.downloader import Wget

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)

    def configure(self):
        pass

    def build(self):
        from pprof.project import clang_cxx
        from plumbum.cmd import gcc

        with local.cwd(self.builddir):
            myclang = clang_cxx()["-fopenmp", self.cflags, "-o",
                                  self.run_f, self.ldflags]
            myclang & FG
