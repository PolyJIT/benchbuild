#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local
import logging

class SDCC(PprofGroup):
    class Factory:
        def create(self, exp):
            return SDCC(exp, "sdcc", "compilation")
    ProjectFactory.addFactory("SDCC", Factory())

    def run(self, experiment):
        with local.cwd(self.builddir):
            log.debug("FIXME: invalid LLVM IR, regenerate from source")
            log.debug("FIXME: test incomplete, port from sdcc/Makefile")
            experiment & FG
