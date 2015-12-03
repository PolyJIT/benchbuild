#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory
from pprof.settings import config
from pprof.projects.pprof.group import PprofGroup

from os import path
from plumbum import local


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
        from pprof.utils.compiler import lt_clang, lt_clang_cxx
        from pprof.utils.run import run
        from plumbum.cmd import mkdir

        js_dir = path.join(self.builddir, self.src_dir, "js", "src")
        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags,
                             self.compiler_extension)
            clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                     self.compiler_extension)
        with local.cwd(js_dir):
            autoconf = local["autoconf"]
            autoconf()
            mkdir("build_OPT.OBJ")
            with local.cwd("build_OPT.OBJ"):
                with local.env(CC=str(clang), CXX=str(clang_cxx)):
                    configure = local["../configure"]
                    run(configure)

    def build(self):
        from plumbum.cmd import make
        from pprof.utils.run import run

        js_dir = path.join(self.builddir, self.src_dir, "js", "src")

        with local.cwd(path.join(js_dir, "build_OPT.OBJ")):
            run(make["-j", config["available_cpu_count"]])

    def run_tests(self, experiment):
        from pprof.project import wrap
        from plumbum.cmd import make
        from pprof.utils.run import run

        js_dir = path.join(self.builddir, self.src_dir, "js", "src")
        js_build_dir = path.join(js_dir, "build_OPT.OBJ")
        wrap(path.join(js_build_dir, "bin", "js"), experiment)

        with local.cwd(js_build_dir):
            run(make["check"])
