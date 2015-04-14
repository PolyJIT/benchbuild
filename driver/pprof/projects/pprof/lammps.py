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

    src_dir = "lammps.git"
    src_uri = "https://github.com/lammps/lammps"

    def download(self):
        from plumbum.cmd import git
        from pprof.project import clang, clang_cxx, llvm_libs, llvm

        with local.cwd(self.builddir):
            git("clone", "--depth", "1", self.src_uri, self.src_dir) 

    def configure(self):
        pass

    def build(self):
        pass
