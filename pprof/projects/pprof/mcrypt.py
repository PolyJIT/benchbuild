#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local

class MCryptAES(PprofGroup):

    """ mcrypt-aes benchmark """

    class Factory:
        def create(self, exp):
            obj = MCryptAES(exp, "mcrypt-aes", "encryption")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("MCryptAES", Factory())

class MCryptCiphers(PprofGroup):

    """ mcrypt-ciphers benchmark """

    class Factory:
        def create(self, exp):
            obj = MCryptCiphers(exp, "mcrypt-ciphers", "encryption")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("MCryptCiphers", Factory())

