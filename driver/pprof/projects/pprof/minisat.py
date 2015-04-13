#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from glob import glob
from plumbum import FG, local

class Minisat(PprofGroup):

    """ minisat benchmark """

    class Factory:
        def create(self, exp):
            obj = Minisat(exp, "minisat", "verification")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Minisat", Factory())

    def run(self, experiment):
        testfiles = glob(path.join(self.testdir, "*.cnf.gz"))
        for f in testfiles:
            with local.cwd(self.builddir):
                (experiment < f) & FG(retcode=[10,20])

