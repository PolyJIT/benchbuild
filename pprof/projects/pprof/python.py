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
            return Python(exp, "python", "compilation")
    ProjectFactory.addFactory("Python", Factory())

    src_dir = "Python-3.4.3"
    src_file = src_dir + ".tar.xz"
    src_uri = "https://www.python.org/ftp/python/3.4.3/" + src_file

    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import tar

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar("xfJ", self.src_file)

    def configure(self):
        from pprof.utils.compiler import clang, clang_cxx
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

    def run_tests(self, experiment):
        from plumbum.cmd import make
        from pprof.project import wrap_tool

        python_dir = path.join(self.builddir, self.src_dir)
        exp = wrap_tool(path.join(python_dir, "python")

        with local.cwd(python_dir):
            make("TESTPYTHON=" + str(exp), "-i", "test")

        #testfiles = find(self.testdir, "-name", "*.py").splitlines()
        # for f in testfiles:
        #    with local.env(PYTHONPATH=self.testdir,
        #                   PYTHONHOME=self.testdir):
        #        experiment[f] & FG(retcode=None)
