#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local
from plumbum.cmd import find

class Python(PprofGroup):

    """ python benchmarks """

    class Factory:
        def create(self, exp):
            obj = Python(exp, "python", "compilation")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Python", Factory())

    src_dir = "Python-3.4.3"
    src_file = src_dir + ".tar.xz"
    src_uri = "https://www.python.org/ftp/python/3.4.3/" + src_file
    def download(self):
        from plumbum.cmd import wget, tar

        with local.cwd(self.builddir):
            wget(self.src_uri)
            tar("xf", self.src_file)

    def configure(self):
        from pprof.project import clang, clang_cxx
        python_dir = path.join(self.builddir, self.src_dir)

        with local.cwd(python_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang()), CXX=str(clang_cxx),
                           CFLAGS=" ".join(self.cflags),
                           LIBS=" ".join(self.ldflags)):
                configure("--disable-shared", "--without-gcc")

    def build(self):
        from plumbum.cmd import make, ln
        python_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(python_dir):
            make & FG

        self.run_f = path.join(python_dir, "python")


    def run_tests(self, experiment):
        from plumbum.cmd import make
        python_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(python_dir):
            make("TESTPYTHON=" + str(experiment), "-i", "test")

        #testfiles = find(self.testdir, "-name", "*.py").splitlines()
        #for f in testfiles:
        #    with local.env(PYTHONPATH=self.testdir,
        #                   PYTHONHOME=self.testdir):
        #        experiment[f] & FG(retcode=None)

