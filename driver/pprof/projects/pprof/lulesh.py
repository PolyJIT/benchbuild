#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local


class Lulesh(PprofGroup):

    """ Lulesh """

    class Factory:
        def create(self, exp):
            obj = Lulesh(exp, "lulesh", "scientific")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Lulesh", Factory())

    @log_with(log)
    def run(self, experiment):
        with local.cwd(self.builddir):
            experiment["20"] & FG

    src_file = "LULESH.cc"
    src_uri = "https://codesign.llnl.gov/lulesh/" + src_file
    def download(self):
        from plumbum.cmd import wget

        with local.cwd(self.builddir):
            wget(self.src_uri)

    def configure(self):
        pass

    def build(self):
        from pprof.project import clang_cxx

        with local.cwd(self.builddir):
            myclang = clang_cxx()[self.cflags, "-o", self.run_f, self.ldflags,
                    self.src_file]
            print myclang
            myclang()

