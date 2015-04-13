#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local
from plumbum.cmd import cat

class Crafty(PprofGroup):

    """ crafty benchmark """

    class Factory:
        def create(self, exp):
            obj = Crafty(exp, "crafty", "scientific")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Crafty", Factory())

    def run(self, experiment):
        with local.cwd(self.builddir):
            (cat[path.join(self.testdir, "test1.sh")] | experiment) & FG
            (cat[path.join(self.testdir, "test2.sh")] | experiment) & FG

