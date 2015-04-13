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
            experiment["-f", "-k", "--best", "text.html"] & FG
            experiment["-f", "-k", "--best", "chicken.jpg"] & FG
            experiment["-f", "-k", "--best", "control"] & FG
            experiment["-f", "-k", "--best", "input.source"] & FG
            experiment["-f", "-k", "--best", "liberty.jpg"] & FG

            # Decompress
            experiment["-f", "-k", "--decompress", "text.html.gz"] & FG
            experiment["-f", "-k", "--decompress", "chicken.jpg.gz"] & FG
            experiment["-f", "-k", "--decompress", "control.gz"] & FG
            experiment["-f", "-k", "--decompress", "input.source.gz"] & FG
            experiment["-f", "-k", "--decompress", "liberty.jpg.gz"] & FG

