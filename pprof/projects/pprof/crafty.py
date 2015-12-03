#!/usr/bin/evn python
#

from pprof.project import ProjectFactory
from pprof.projects.pprof.group import PprofGroup

from os import path
from plumbum import local
from plumbum.cmd import cat


class Crafty(PprofGroup):
    """ crafty benchmark """

    class Factory:
        def create(self, exp):
            return Crafty(exp, "crafty", "scientific")

    ProjectFactory.addFactory("Crafty", Factory())

    src_dir = "crafty-23.4"
    src_file = src_dir + ".zip"
    src_uri = "http://www.craftychess.com/crafty-23.4.zip"

    def download(self):
        from pprof.utils.downloader import Wget
        from plumbum.cmd import unzip, mv

        book_file = "book.bin"
        book_bin = "http://www.craftychess.com/" + book_file
        with local.cwd(self.builddir):
            Wget(self.src_uri, self.src_file)
            Wget(book_bin, "book.bin")

            unzip(self.src_file)
            mv(book_file, self.src_dir)

    def configure(self):
        pass

    def build(self):
        from plumbum.cmd import make
        from pprof.utils.compiler import lt_clang, lt_clang_cxx
        from pprof.utils.run import run

        crafty_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(crafty_dir):
            target_opts = ["-DINLINE64", "-DCPUS=1"]

            with local.cwd(self.builddir):
                clang = lt_clang(self.cflags, self.ldflags,
                                 self.compiler_extension)
                clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                         self.compiler_extension)

            run(make["target=LINUX", "CC=" + str(clang), "CXX=" + str(
                clang_cxx), "opt=" + " ".join(target_opts), "crafty-make"])

    def run_tests(self, experiment):
        from pprof.project import wrap
        from pprof.utils.run import run
        crafty_dir = path.join(self.builddir, self.src_dir)
        exp = wrap(path.join(crafty_dir, "crafty"), experiment)

        run((cat[path.join(self.testdir, "test1.sh")] | exp))
        run((cat[path.join(self.testdir, "test2.sh")] | exp))
