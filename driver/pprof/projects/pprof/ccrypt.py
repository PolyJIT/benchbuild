#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local
from plumbum.cmd import ln

class Ccrypt(PprofGroup):

    """ ccrypt benchmark """

    check_f = "check"

    class Factory:
        def create(self, exp):
            obj = Ccrypt(exp, "ccrypt", "encryption")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Ccrypt", Factory())

    def prepare(self):
        super(Ccrypt, self).prepare()
        check_f = path.join(self.testdir, self.check_f)
        ln("-s", check_f, path.join(self.builddir, self.check_f))

    def clean(self):
        check_f = path.join(self.builddir, self.check_f)
        self.products.add(check_f)

        super(Ccrypt, self).clean()

    def run(self, experiment):
        with local.cwd(self.builddir):
            command = " ".join(experiment["-f"].formulate())
            crypt_check = path.join(self.builddir, "check", "ccrypt-check.sh")
            length_check = path.join(self.builddir, "check", "length-check.sh")
            with local.env(CCRYPT=command,
                           srcdir=path.join(self.builddir, "check")):
                local[crypt_check] & FG
                local[length_check] & FG

