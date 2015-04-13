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

    @log_with(log)
    def prepare(self):
        super(Bzip2, self).prepare()
        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        cp[testfiles, self.builddir] & FG

    @log_with(log)
    def run(self, experiment):
        with local.cwd(self.builddir):
            # Compress
            experiment["-f", "-z", "-k", "--best", "text.html"] & FG
            experiment["-f", "-z", "-k", "--best", "chicken.jpg"] & FG
            experiment["-f", "-z", "-k", "--best", "control"] & FG
            experiment["-f", "-z", "-k", "--best", "input.source"] & FG
            experiment["-f", "-z", "-k", "--best", "liberty.jpg"] & FG

            # Decompress
            experiment["-f", "-k", "--decompress", "text.html.bz2"] & FG
            experiment["-f", "-k", "--decompress", "chicken.jpg.bz2"] & FG
            experiment["-f", "-k", "--decompress", "control.bz2"] & FG
            experiment["-f", "-k", "--decompress", "input.source.bz2"] & FG
            experiment["-f", "-k", "--decompress", "liberty.jpg.bz2"] & FG

