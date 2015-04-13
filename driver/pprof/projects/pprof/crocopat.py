#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from glob import glob
from plumbum import FG, local
from plumbum.cmd import cat

class Crocopat(PprofGroup):

    """ crocopat benchmark """

    class Factory:
        def create(self, exp):
            obj = Crocopat(exp, "crocopat", "verification")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Crocopat", Factory())

    def run(self, experiment):
        with local.cwd(self.builddir):
            programs = glob(path.join(self.testdir, "programs", "*.rml"))
            projects = glob(path.join(self.testdir, "projects", "*.rsf"))
            for program in programs:
                for project in projects:
                    (cat[project] | experiment[program]) & FG(retcode=None)
