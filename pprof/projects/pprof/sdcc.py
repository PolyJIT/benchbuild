#!/usr/bin/evn python
#

from pprof.project import ProjectFactory
from pprof.settings import config
from pprof.projects.pprof.group import PprofGroup

from os import path
from plumbum import FG, local


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
        from pprof.utils.run import run

        sdcc_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(self.builddir):
            clang = lt_clang(self.cflags, self.ldflags,
                             self.compiler_extension)
            clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                     self.compiler_extension)

        with local.cwd(sdcc_dir):
            configure = local["./configure"]
            with local.env(CC=str(clang), CXX=str(clang_cxx)):
                run(configure["--without-ccache", "--disable-pic14-port",
                              "--disable-pic16-port"])

    def build(self):
        from plumbum.cmd import make
        from pprof.utils.run import run
        sdcc_dir = path.join(self.builddir, self.src_dir)

        with local.cwd(sdcc_dir):
            run(make["-j", config["jobs"]])

    def run_tests(self, experiment):
        from pprof.project import wrap
        from pprof.utils.run import run

        exp = wrap(self.run_f, experiment(self.run_f))
        run(exp)
