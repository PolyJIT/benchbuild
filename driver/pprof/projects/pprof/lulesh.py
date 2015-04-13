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

    def run(self, experiment):
        with local.cwd(self.builddir):
            experiment["20"] & FG


