#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory
from pprof.projects.pprof.group import PprofGroup
from plumbum import local


class Lulesh(PprofGroup):

    """ Lulesh """

    class Factory:

        def create(self, exp):
            return Lulesh(exp, "lulesh", "scientific")
    ProjectFactory.addFactory("Lulesh", Factory())

    def run_tests(self, experiment):
        from pprof.project import wrap

        exp = wrap(self.run_f, experiment)
        for i in range(1, 10):
            exp(str(i))

    src_file = "LULESH.cc"
    src_uri = "https://codesign.llnl.gov/lulesh/" + src_file

    def download(self):
        from pprof.utils.downloader import Wget

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)

    def configure(self):
        pass

    def build(self):
        from pprof.utils.compiler import lt_clang_cxx

        with local.cwd(self.builddir):
            clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                     self.compiler_extension)
            clang_cxx("-o", self.run_f, self.src_file)
