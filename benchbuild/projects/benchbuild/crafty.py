from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import cat, make, mkdir, mv, unzip
from benchbuild.utils.compiler import cc
from benchbuild.utils.downloader import Wget, with_wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


@with_wget({
    "25.2":
    "http://www.craftychess.com/downloads/source/crafty-25.2.zip"
})
class Crafty(Project):
    """ crafty benchmark """

    NAME = 'crafty'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    VERSION = '25.2'
    SRC_FILE = "crafty.zip"

    def compile(self):
        self.download()
        book_file = "book.bin"
        book_bin = "http://www.craftychess.com/downloads/book/" + book_file
        Wget(book_bin, book_file)

        unpack_dir = "crafty.src"
        mkdir(unpack_dir)

        with local.cwd(unpack_dir):
            unzip(path.join("..", self.src_file))
        mv(book_file, unpack_dir)

        clang = cc(self)
        with local.cwd(unpack_dir):
            target_opts = ["-DCPUS=1", "-DSYZYGY", "-DTEST"]
            crafty_make = make["target=UNIX", "CC=" + str(clang), "opt=" +
                               " ".join(target_opts), "crafty-make"]
            run(crafty_make)

    def run_tests(self, runner):
        unpack_dir = "crafty.src"
        with local.cwd(unpack_dir):
            exp = wrap("./crafty", self)
            runner(
                (cat[path.join(self.testdir, "test1.sh")] | exp),
                retcode=[0, 120])
            runner(
                (cat[path.join(self.testdir, "test2.sh")] | exp),
                retcode=[0, 120])
