#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory
from pprof.projects.pprof.group import PprofGroup

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
        from pprof.utils.compiler import lt_clang, lt_clang_cxx
        python_dir = path.join(self.builddir, self.src_dir)

        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags)
            clang_cxx = lt_clang_cxx(self.cflags, self.ldflags)

        with local.cwd(python_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                configure("--disable-shared", "--without-gcc")

    def build(self):
        from plumbum.cmd import make
        python_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(python_dir):
            make()

    def run_tests(self, experiment):
        from plumbum.cmd import make
        from pprof.project import wrap

        python_dir = path.join(self.builddir, self.src_dir)
        exp = wrap(path.join(python_dir, "python"), experiment)

        with local.cwd(python_dir):
            make("TESTPYTHON=" + str(exp), "-i", "test")
