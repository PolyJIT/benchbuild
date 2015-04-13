#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from glob import glob

from plumbum import FG, local
from plumbum.cmd import cp, echo, chmod, make

class LibAV(PprofGroup):

    """ LibAV benchmark """

    class Factory:
        def create(self, exp):
            return LibAV(exp, "avconv", "multimedia")
    ProjectFactory.addFactory("LibAV", Factory())

    @log_with(log)
    def clean(self):
        testfiles = path.join(self.testdir)
        btestfiles = glob(path.join(self.builddir, "*"))

        self.products.add(path.join(self.builddir, "tests"))
        for f in btestfiles:
            if not path.isdir(f):
                self.products.add(f)

        self.products.add(path.join(self.builddir, "Makefile.libav"))
        super(LibAV, self).clean()

    @log_with(log)
    def prepare(self):
        super(LibAV, self).prepare()

        testfiles = glob(path.join(self.testdir, "*"))

        for f in testfiles:
            cp["-a", f, self.builddir] & FG
        cp[path.join(self.sourcedir, "Makefile.libav"), self.builddir] & FG

    @log_with(log)
    def run(self, experiment):
        with local.cwd(self.builddir):
            with local.env(TESTDIR=self.builddir):
                echo["#!/bin/sh"] >> path.join(self.builddir, self.name) & FG
                echo[str(experiment)] >> path.join(self.builddir, self.name) & FG
                chmod["+x", path.join(self.builddir, self.name)] & FG
                make["-i", "-f", "Makefile.libav", "fate"] & FG

