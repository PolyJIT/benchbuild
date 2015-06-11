#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory
from pprof.projects.pprof.group import PprofGroup
from plumbum import local


class LuleshOMP(PprofGroup):

    """ Lulesh-OMP """

    class Factory:

        def create(self, exp):
            return LuleshOMP(exp, "lulesh-omp", "scientific")
    ProjectFactory.addFactory("LuleshOMP", Factory())

    def run_tests(self, experiment):
        from pprof.project import wrap
        exp = wrap(self.run_f, experiment)
        exp("10")

    src_file = "LULESH_OMP.cc"
    src_uri = "https://codesign.llnl.gov/lulesh/" + src_file

    def download(self):
        from pprof.utils.downloader import Wget

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)

    def configure(self):
        pass

    def build(self):
        from pprof.utils.compiler import lt_clang_cxx
        self.ldflags += ["-lgomp"]

        with local.cwd(self.builddir):
            clang_cxx = lt_clang_cxx(self.cflags, self.ldflags)
            clang_cxx("-o", self.run_f, self.src_file)
