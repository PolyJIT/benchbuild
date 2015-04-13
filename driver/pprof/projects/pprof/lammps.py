#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from glob import glob
from plumbum import FG, local

class Lammps(PprofGroup):

    """ LAMMPS benchmark """

    class Factory:
        def create(self, exp):
            return Lammps(exp, "lammps", "scientific")
    ProjectFactory.addFactory("Lammps", Factory())

    def run(self, experiment):
        with local.cwd(self.builddir):
            tests = glob(path.join(self.testdir, "in.*"))
            for test in tests:
                (experiment < test) & FG

