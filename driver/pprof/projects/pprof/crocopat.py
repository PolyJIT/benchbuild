#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from glob import glob
from plumbum import FG, local
from plumbum.cmd import cat

class Crocopat(PprofGroup):

    """ crocopat benchmark """

    class Factory:
        def create(self, exp):
            obj = Crocopat(exp, "crocopat", "verification")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Crocopat", Factory())

    def run(self, experiment):
        with local.cwd(self.builddir):
            programs = glob(path.join(self.testdir, "programs", "*.rml"))
            projects = glob(path.join(self.testdir, "projects", "*.rsf"))
            for program in programs:
                for project in projects:
                    (cat[project] | experiment[program]) & FG(retcode=None)

    src_dir = "crocopat-2.1.4"
    src_file = src_dir + ".zip"
    src_uri = "http://crocopat.googlecode.com/files/" + src_file
    def download(self):
        from plumbum.cmd import wget, unzip

        crocopat_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(self.builddir):
            wget(self.src_uri)
            unzip(path.join(self.builddir, self.src_file))

    def configure(self):
        pass

    def build(self):
        from plumbum.cmd import make
        from pprof.project import clang_cxx

        crocopat_dir = path.join(self.builddir, self.src_dir, "src")
        with local.cwd(crocopat_dir):
            cflags = self.cflags + ["-I.", "-ansi"]
            ldflags = self.ldflags + ["-L.", "-lrelbdd"]
            make["CXX=" + str(clang_cxx()),
                 "CFLAGS=" + " ".join(cflags),
                 "LFLAGS=" + " ".join(ldflags)] & FG

