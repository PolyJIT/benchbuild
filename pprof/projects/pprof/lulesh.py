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
            return Lulesh(exp, "lulesh", "scientific")
    ProjectFactory.addFactory("Lulesh", Factory())

    @log_with(log)
    def run_tests(self, experiment):
        exp = experiment(self.run_f)
        exp["10"] & FG

    src_file = "LULESH.cc"
    src_uri = "https://codesign.llnl.gov/lulesh/" + src_file

    def download(self):
        from pprof.utils.downloader import Wget

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)

    def configure(self):
        pass

    def build(self):
        from pprof.utils.compiler import clang_cxx

        with local.cwd(self.builddir):
            clang_cxx()[
                self.cflags, "-o", self.run_f, self.ldflags, self.src_file] & FG
