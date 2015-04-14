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

    def run(self, experiment):
        with local.cwd(self.builddir):
            experiment["20"] & FG

    src_file = "LULESH_OMP.cc"
    src_uri = "https://codesign.llnl.gov/lulesh/" + src_file
    def download(self):
        from plumbum.cmd import wget

        with local.cwd(self.builddir):
            wget(self.src_uri)

    def configure(self):
        pass

    def build(self):
        from pprof.project import clang_cxx
        from plumbum.cmd import gcc

        with local.cwd(self.builddir):
            myclang = clang_cxx()["-fopenmp", self.cflags, "-o",
                                  self.run_f, self.ldflags]
            ( gcc["-E", "-fopenmp", self.cflags, self.src_file] | myclang ) & FG
