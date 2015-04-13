#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local
from plumbum.cmd import cp

class XZ(PprofGroup):

    """ XZ """

    testfiles = ["text.html", "chicken.jpg", "control", "input.source",
                 "liberty.jpg"]

    class Factory:
        def create(self, exp):
            obj = XZ(exp, "xz", "compression")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("XZ", Factory())

    def clean(self):
        for x in self.testfiles:
            self.products.add(path.join(self.builddir, x))
            self.products.add(path.join(self.builddir, x + ".xz"))

        super(XZ, self).clean()

    def prepare(self):
        super(XZ, self).prepare()
        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        cp[testfiles, self.builddir] & FG

    def run(self, experiment):
        with local.cwd(self.builddir):
            # Compress
            experiment["-f", "-k", "--compress", "-e", "-9", "text.html"] & FG
            experiment["-f", "-k", "--compress", "-e", "-9", "chicken.jpg"] & FG
            experiment["-f", "-k", "--compress", "-e", "-9", "control"] & FG
            experiment[
                "-f",
                "-k",
                "--compress",
                "-e",
                "-9",
                "input.source"] & FG
            experiment["-f", "-k", "--compress", "-e", "-9", "liberty.jpg"] & FG

            # Decompress
            experiment["-f", "-k", "--decompress", "text.html.xz"] & FG
            experiment["-f", "-k", "--decompress", "chicken.jpg.xz"] & FG
            experiment["-f", "-k", "--decompress", "control.xz"] & FG
            experiment["-f", "-k", "--decompress", "input.source.xz"] & FG
            experiment["-f", "-k", "--decompress", "liberty.jpg.xz"] & FG

