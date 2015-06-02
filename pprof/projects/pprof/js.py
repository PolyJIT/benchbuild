#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log
from pprof.settings import config
from group import PprofGroup

from os import path
from glob import glob
from plumbum import FG, local
from plumbum.cmd import chmod, echo, cp


class SpiderMonkey(PprofGroup):

    class Factory:

        def create(self, exp):
            return SpiderMonkey(exp, "js", "compilation")
    ProjectFactory.addFactory("SpiderMonkey", Factory())

    src_uri = "https://github.com/mozilla/gecko-dev.git"
    src_dir = "gecko-dev.git"

    def download(self):
        from pprof.utils.downloader import Git

        with local.cwd(self.builddir):
            Git(self.src_uri, self.src_dir)

    def configure(self):
        from pprof.utils.compiler import clang, clang_cxx
        from plumbum.cmd import mkdir
        js_dir = path.join(self.builddir, self.src_dir, "js", "src")
        with local.cwd(js_dir):
            autoconf = local["autoconf_2.13"]
            autoconf()
            mkdir("build_OPT.OBJ")
            with local.cwd("build_OPT.OBJ"):
                with local.env(CC=clang(),
                               CXX=clang_cxx(),
                               CFLAGS=" ".join(self.cflags),
                               LDFLAGS=" ".join(self.ldflags),
                               CXXFLAGS=" ".join(self.cflags)):
                    configure = local["../configure"]
                    configure()

    def build(self):
        from plumbum.cmd import make
        js_dir = path.join(self.builddir, self.src_dir, "js", "src")

        with local.cwd(path.join(js_dir, "build_OPT.OBJ")):
            make("-j", config["available_cpu_count"])

    def run_tests(self, experiment):
        from pprof import wrap
        from plumbum.cmd import make

        js_dir = path.join(self.builddir, self.src_dir, "js", "src")
        js_build_dir = path.join(js_dir, "build_OPT.OBJ")
        exp = wrap(path.join(js_build_dir, "bin", "js"), experiment)

        with local.cwd(js_build_dir):
            make("check")
