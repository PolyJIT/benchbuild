#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local
from plumbum.cmd import chmod

class Ruby(PprofGroup):
    class Factory:
        def create(self, exp):
            obj = Ruby(exp, "ruby", "compilation")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Ruby", Factory())

    src_dir = "ruby-2.2.2"
    src_file = src_dir + ".tar.gz"
    src_uri = "http://cache.ruby-lang.org/pub/ruby/2.2/" + src_file
    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import tar

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar("xfz", self.src_file)

    def configure(self):
        from pprof.project import clang, clang_cxx
        ruby_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(ruby_dir):
            with local.env(CC=str(clang()), CXX=str(clang_cxx),
                           CFLAGS=" ".join(self.cflags),
                           LIBS=" ".join(self.ldflags)):
                configure = local["./configure"]
                configure["--with-static-linked-ext", "--disable-shared"] & FG

    def build(self):
        from plumbum.cmd import make, ln

        ruby_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(ruby_dir):
            make & FG

        with local.cwd(self.builddir):
            ln("-sf", path.join(ruby_dir, "ruby"), self.bin_f)

    def run_tests(self, experiment):
        from plumbum.cmd import ruby, echo, chmod

        with local.env(RUBYOPT=""):
            sh_script = path.join(self.builddir, self.bin_f + ".sh")
            (echo["#!/bin/sh"] > sh_script) & FG
            (echo[str(experiment) + " $*"] >> sh_script) & FG
            chmod("+x", sh_script)

            ruby[path.join(self.testdir, "benchmark", "run.rb"),
                 "--ruby=\""+str(sh_script)+"\"",
                 "--opts=\"-I"+path.join(self.testdir, "lib") +
                 " -I"+path.join(self.testdir, ".")+
                 " -I"+path.join(self.testdir, ".ext", "common")+
                 "\"", "-r"] & FG
