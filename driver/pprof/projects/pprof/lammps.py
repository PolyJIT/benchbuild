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

    def prepare(self):
        super(PprofGroup, self).prepare()
        from plumbum.cmd import cp
        
        with local.cwd(self.builddir):
            cp("-vr", self.testdir, "test")

    def run_tests(self, experiment):
        with local.cwd(path.join(self.builddir, "test")):
            tests = glob(path.join(self.testdir, "in.*"))
            for test in tests:
                cmd = (experiment < test)
                cmd & FG(retcode=None)

    src_dir = "lammps.git"
    src_uri = "https://github.com/lammps/lammps"

    def download(self):
        from pprof.utils.downloader import Git

        with local.cwd(self.builddir):
            Git(self.src_uri, self.src_dir)

    def configure(self):
        pass

    def build(self):
        from plumbum.cmd import make, ln
        from pprof.project import clang_cxx, clang

        with local.cwd(path.join(self.builddir, self.src_dir, "src")):
            make["CC=" + str(clang_cxx()),
                 "CCFLAGS=" + " ".join(self.cflags),
                 "LINKFLAGS=" + " ".join(self.ldflags), "-j4",
                 "clean", "serial"] & FG

        lammps_dir = path.join(self.builddir, self.src_dir, "src")
        with local.cwd(self.builddir):
            ln("-sf", path.join(lammps_dir, "lmp_serial"), self.run_f)
