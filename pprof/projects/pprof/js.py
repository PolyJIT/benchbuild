#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from glob import glob
from plumbum import FG, local
from plumbum.cmd import chmod, echo, cp


class SpiderMonkey(PprofGroup):

    class Factory:

        def create(self, exp):
            return SpiderMonkey(exp, "js", "compilation")
    ProjectFactory.addFactory("SpiderMonkey", Factory())

    def prepare(self):
        super(SpiderMonkey, self).prepare()
        config_path = path.join(self.testdir, "config")
        cp["-var", config_path, self.builddir] & FG
        self.products.add(path.join(config_path, "autoconf.mk"))
        self.products.add(config_path)

    def run_tests(self, experiment):
        exp = experiment(self.run_f)

        for jsfile in glob(path.join(self.testdir, "sunspider", "*.js")):
            (exp < jsfile) & FG

        sh_script = path.join(self.builddir, self.bin_f + ".sh")
        (echo["#!/bin/sh"] > sh_script) & FG
        (echo[str(exp) + " $*"] >> sh_script) & FG
        chmod("+x", sh_script)
        jstests = local[path.join(self.testdir, "tests", "jstests.py")]
        jstests[sh_script] & FG(retcode=None)
