#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local

class Linpack(PprofGroup):

    """ Linpack (C-Version) """

    class Factory:
        def create(self, exp):
            obj = Linpack(exp, "linpack", "scientific")

            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")

            return obj
    ProjectFactory.addFactory("Linpack", Factory())

    src_uri = "http://www.netlib.org/benchmark/linpackc.new"
    def download(self):
        from plumbum.cmd import wget, patch
        
        lp_patch = path.join(self.sourcedir, "linpack.patch")
        with local.cwd(self.builddir):
            wget("-O", path.join(self.builddir, "linpack.c"), self.src_uri)
            (patch["-p0"] < lp_patch)() 
        
    def configure(self):
        pass

    def build(self):
        from pprof.settings import config

        cflags = self.cflags
        ldflags = self.ldflags + ["-lm"]
        llvm = path.join(config["llvmdir"], "bin")
        llvm_libs = path.join(config["llvmdir"], "lib")

        clang = local[path.join(llvm, "clang")]
        with local.cwd(self.builddir):
            with local.env(LD_LIBRARY_PATH=llvm_libs):
                clang[cflags,
                      ldflags,
                      "-o", self.run_f,
                      "linpack.c"] & FG

