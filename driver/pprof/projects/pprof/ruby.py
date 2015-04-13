#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local
from plumbum.cmd import chmod

class Ruby(PprofGroup):
    class Factory:
        def create(self, exp):
            obj = Ruby(exp, "ruby", "compilation")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Ruby", Factory())

    def run(self, experiment):
        from plumbum.cmd import ruby

        with local.cwd(self.builddir):
            with local.env(RUBYOPT=""):
                sh_script = path.join(self.builddir, self.bin_f + ".sh")
                (echo["#!/bin/sh"] > sh_script) & FG
                (echo[str(experiment) + " $*"] >> sh_script) & FG
                chmod("+x", sh_script)

                ruby[path.join(self.testdir, "benchmark", "run.rb"),
                     "--ruby=\""+str(sh_script)+"\"",
                     "--opts=\"-I"+path.join(self.testdir, "lib") +
                     " -I"+path.join(self.testdir, ".")+
                     " -I"+path.join(self.testdir, ".ext", "common")+
                     "\"", "-r"] & FG
