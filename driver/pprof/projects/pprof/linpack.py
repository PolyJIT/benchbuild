#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local

class Linpack(PprofGroup):

    """ Linpack (C-Version) """

    class Factory:
        def create(self, exp):
            obj = Linpack(exp, "linpack", "scientific")

            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")

            return obj
    ProjectFactory.addFactory("Linpack", Factory())

