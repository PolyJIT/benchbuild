#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local

class SQLite3(PprofGroup):

    """ SQLite3 """

    class Factory:
        def create(self, exp):
            obj = SQLite3(exp, "sqlite3", "database")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("SQLite3", Factory())

