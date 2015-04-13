#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local

class SevenZip(PprofGroup):

    """ 7Zip """

    class Factory:
        def create(self, exp):
            obj = SevenZip(exp, "7z", "compression")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("SevenZip", Factory())

    def run(self, experiment):
        with local.cwd(self.builddir):
            experiment["b", "-mmt1"] & FG
