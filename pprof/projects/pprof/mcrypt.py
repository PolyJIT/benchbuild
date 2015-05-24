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
            return MCryptAES(exp, "mcrypt-aes", "encryption")
    ProjectFactory.addFactory("MCryptAES", Factory())


class MCryptCiphers(PprofGroup):

    """ mcrypt-ciphers benchmark """

    class Factory:

        def create(self, exp):
            return MCryptCiphers(exp, "mcrypt-ciphers", "encryption")
    ProjectFactory.addFactory("MCryptCiphers", Factory())
