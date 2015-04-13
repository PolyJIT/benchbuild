#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local
from plumbum.cmd import find

class Python(PprofGroup):

    """ python benchmarks """

    class Factory:
        def create(self, exp):
            obj = Python(exp, "python", "compilation")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Python", Factory())

    def run(self, experiment):
        testfiles = find(self.testdir, "-name", "*.py").splitlines()
        for f in testfiles:
            with local.env(PYTHONPATH=self.testdir,
                           PYTHONHOME=self.testdir):
                with local.cwd(self.builddir):
                    experiment[f] & FG(retcode=None)

