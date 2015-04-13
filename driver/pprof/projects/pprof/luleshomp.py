#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local

class LuleshOMP(PprofGroup):

    """ Lulesh-OMP """

    class Factory:
        def create(self, exp):
            return LuleshOMP(exp, "lulesh-omp", "scientific")
    ProjectFactory.addFactory("LuleshOMP", Factory())

    def run(self, experiment):
        with local.cwd(self.builddir):
            experiment["20"] & FG

