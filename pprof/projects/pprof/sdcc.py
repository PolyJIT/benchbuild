#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local
import logging


class SDCC(PprofGroup):

    class Factory:

        def create(self, exp):
            return SDCC(exp, "sdcc", "compilation")
    ProjectFactory.addFactory("SDCC", Factory())

    src_dir = "sdcc"
    src_uri = "svn://svn.code.sf.net/p/sdcc/code/trunk/" + src_dir

    def download(self):
        from pprof.utils.downloader import Svn

        with local.cwd(self.builddir):
            Svn(self.src_uri, self.src_dir)

    def configure(self):
        from pprof.utils.compiler import lt_clang, lt_clang_cxx

        sdcc_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(sdcc_dir):
            configure = local["./configure"]
            with local.env(CC=str(lt_clang(self.cflags, self.ldflags)),
                           CXX=str(lt_clang_cxx(self.cflags, self.ldflags)),
                           CFLAGS=" ".join(self.cflags),
                           CXXFLAGS=" ".join(self.cflags),
                           LIBS=" ".join(self.ldflags)):
                configure("--without-ccache", "--disable-pic14-port",
                          "--disable-pic16-port")

    def build(self):
        from plumbum.cmd import make
        sdcc_dir = path.join(self.builddir, self.src_dir)

        with local.cwd(sdcc_dir):
            make()

    def run_tests(self, experiment):
        from plumbum.cmd import make
        from pprof.project import wrap_tool

        import pdb
        pdb.set_trace()
        exp = experiment(self.run_f)

        log.debug("FIXME: invalid LLVM IR, regenerate from source")
        log.debug("FIXME: test incomplete, port from sdcc/Makefile")
        exp & FG
