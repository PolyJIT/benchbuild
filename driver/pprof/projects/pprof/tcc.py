#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local

import logging


class TCC(PprofGroup):
    class Factory:
        def create(self, exp):
            return TCC(exp, "tcc", "compilation")
    ProjectFactory.addFactory("TCC", Factory())

    def run(self, experiment):
        with local.cwd(self.builddir):
            log.debug("FIXME: test incomplete, port from tcc/Makefile")
            experiment & FG

