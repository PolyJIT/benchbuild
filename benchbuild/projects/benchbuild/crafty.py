from benchbuild.project import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang, lt_clang_cxx
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from os import path
from plumbum import local
from plumbum.cmd import cat, make, unzip, mv


class Crafty(BenchBuildGroup):
    """ crafty benchmark """

    NAME = 'crafty'
    DOMAIN = 'scientific'

    src_dir = "crafty-23.4"
    src_file = src_dir + ".zip"
    src_uri = "http://www.craftychess.com/crafty-23.4.zip"

    def download(self):
        book_file = "book.bin"
        book_bin = "http://www.craftychess.com/" + book_file
        Wget(self.src_uri, self.src_file)
        Wget(book_bin, "book.bin")

        unzip(self.src_file)
        mv(book_file, self.src_dir)

    def configure(self):
        pass

    def build(self):
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang_cxx = lt_clang_cxx(self.cflags, self.ldflags,
                                 self.compiler_extension)
        with local.cwd(self.src_dir):
            target_opts = ["-DINLINE64", "-DCPUS=1"]

            run(make["target=LINUX", "CC=" + str(clang), "CXX=" + str(
                clang_cxx), "opt=" + " ".join(target_opts), "crafty-make"])

    def run_tests(self, experiment):
        exp = wrap(path.join(self.src_dir, "crafty"), experiment)

        run((cat[path.join(self.testdir, "test1.sh")] | exp))
        run((cat[path.join(self.testdir, "test2.sh")] | exp))
