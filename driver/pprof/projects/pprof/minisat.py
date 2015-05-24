#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from glob import glob
from plumbum import FG, local

class Minisat(PprofGroup):

    """ minisat benchmark """

    class Factory:
        def create(self, exp):
            obj = Minisat(exp, "minisat", "verification")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Minisat", Factory())

    def run_tests(self, experiment):
        from pprof.project import llvm_libs
        exp = experiment(self.run_f)

        testfiles = glob(path.join(self.testdir, "*.cnf.gz"))
        for f in testfiles:
            minisat_dir = path.join(self.builddir, self.src_dir)
            libpath = [
                    path.join(minisat_dir, "build", "dynamic", "lib"),
                    llvm_libs()
                    ]
            with local.env(LD_LIBRARY_PATH=":".join(libpath)):
                (exp < f) & FG(retcode=None)

    src_dir = "minisat.git"
    src_uri = "https://github.com/niklasso/minisat"
    def download(self):
        from pprof.utils.downloader import Git
        from plumbum.cmd import git

        minisat_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(self.builddir):
            Git(self.src_uri, self.src_dir)
            with local.cwd(minisat_dir):
                git("fetch", "origin", "pull/17/head:clang")
                git("checkout", "clang")

    def configure(self):
        from plumbum.cmd import make

        minisat_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(minisat_dir):
            make("config")

    def build(self):
        from plumbum.cmd import make, ln
        from pprof.utils.compiler import clang_cxx, clang, llvm_libs

        minisat_dir = path.join(self.builddir, self.src_dir)
        cflags = " ".join(self.cflags)
        ldflags = " ".join(self.ldflags)
        with local.cwd(minisat_dir):
            with local.env(VERB="1"):
                make("CXX=" + str(clang_cxx()),
                     "CXXFLAGS=" + cflags,
                     "LDFLAGS=" + ldflags,
                     "clean", "lsh", "sh")

        with local.cwd(self.builddir):
            ln("-sf", path.join(minisat_dir, "build", "dynamic", "bin",
               "minisat"), self.run_f)
