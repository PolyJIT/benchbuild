#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory
from pprof.settings import config
from pprof.projects.pprof.group import PprofGroup

from os import path
from plumbum import FG, local
from plumbum.cmd import cp


class Gzip(PprofGroup):

    """ Gzip """

    testfiles = ["text.html", "chicken.jpg", "control", "input.source",
                 "liberty.jpg"]

    class Factory:

        def create(self, exp):
            return Gzip(exp, "gzip", "compression")
    ProjectFactory.addFactory("Gzip", Factory())

    def prepare(self):
        super(Gzip, self).prepare()
        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        cp(testfiles, self.builddir)

    def run_tests(self, experiment):
        from pprof.project import wrap
        from pprof.utils.run import run

        gzip_dir = path.join(self.builddir, self.src_dir)
        exp = wrap(path.join(gzip_dir, "gzip"), experiment)

        # Compress
        run(exp["-f", "-k", "--best", "text.html"])
        run(exp["-f", "-k", "--best", "chicken.jpg"])
        run(exp["-f", "-k", "--best", "control"])
        run(exp["-f", "-k", "--best", "input.source"])
        run(exp["-f", "-k", "--best", "liberty.jpg"])

        # Decompress
        run(exp["-f", "-k", "--decompress", "text.html.gz"])
        run(exp["-f", "-k", "--decompress", "chicken.jpg.gz"])
        run(exp["-f", "-k", "--decompress", "control.gz"])
        run(exp["-f", "-k", "--decompress", "input.source.gz"])
        run(exp["-f", "-k", "--decompress", "liberty.jpg.gz"])

    src_dir = "gzip-1.6"
    src_file = src_dir + ".tar.xz"
    src_uri = "http://ftpmirror.gnu.org/gzip/" + src_file

    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import tar

        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            tar("xfJ", path.join(self.builddir, self.src_file))

    def configure(self):
        from pprof.utils.compiler import lt_clang
        from pprof.utils.run import run

        gzip_dir = path.join(self.builddir, self.src_dir)

        with local.cwd(gzip_dir):
            with local.cwd(self.builddir):
                clang = lt_clang(self.cflags, self.ldflags,
                                 self.compiler_extension)
            configure = local["./configure"]
            with local.env(CC=str(clang)):
                run(configure["--disable-dependency-tracking",
                              "--disable-silent-rules",
                              "--with-gnu-ld"])

    def build(self):
        from plumbum.cmd import make
        from pprof.utils.run import run

        gzip_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(gzip_dir):
            run(make["-j" + config["jobs"], "clean", "all"])
