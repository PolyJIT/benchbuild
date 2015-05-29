#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log
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

    src_dir = "tcc-0.9.26"
    src_file = src_dir + ".tar.bz2"
    src_uri = "http://download-mirror.savannah.gnu.org/releases/tinycc/" + \
        src_file

    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import tar, sed

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar("xjf", self.src_file)

        tcc_dir = path.join(self.builddir, self.src_dir)

    def configure(self):
        from pprof.project import llvm, llvm_libs, clang, mkdir
        tcc_dir = path.join(self.builddir, self.src_dir)

        with local.cwd(self.builddir):
            mkdir("build")
        with local.cwd(path.join(self.builddir, "build")):
            configure = local[path.join(tcc_dir, "configure")]
            configure["--cc=" + str(clang()),
                      "--libdir=/usr/lib64",
                      "--extra-cflags=" + " ".join(self.cflags),
                      "--extra-ldflags=" + " ".join(self.ldflags)] & FG

    def build(self):
        from plumbum.cmd import make, ln

        tcc_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(path.join(self.builddir, "build")):
            make & FG
            make["TCC=" + str(experiment), "test"] & FG

    def run_tests(self, experiment):
        from plumbum.cmd import make

        exp = experiment(self.run_f)

        with local.cwd(self.builddir):
            make["test"] & FG
        log.debug("FIXME: test incomplete, port from tcc/Makefile")
        exp & FG
