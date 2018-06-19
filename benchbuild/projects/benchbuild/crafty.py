from os import path

from plumbum import local

from benchbuild.project import Project
from benchbuild.utils.cmd import cat, make, mkdir, mv, unzip
from benchbuild.utils.compiler import cc
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.wrapping import wrap


class Crafty(Project):
    """ crafty benchmark """

    NAME = 'crafty'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    VERSION = '25.2'

    src_dir = "crafty-{0}".format(VERSION)
    src_uri = "http://www.craftychess.com/" \
              "downloads/source/crafty-{0}.zip".format(VERSION)
    SRC_FILE = src_dir + ".zip"

    def download(self):
        book_file = "book.bin"
        book_bin = "http://www.craftychess.com/downloads/book/" + book_file
        Wget(self.src_uri, self.SRC_FILE)
        Wget(book_bin, book_file)

        mkdir(self.src_dir)

        with local.cwd(self.src_dir):
            unzip(path.join("..", self.SRC_FILE))
        mv(book_file, self.src_dir)

    def configure(self):
        pass

    def build(self):
        clang = cc(self)
        with local.cwd(self.src_dir):
            target_opts = ["-DCPUS=1", "-DSYZYGY", "-DTEST"]
            crafty_make = make["target=UNIX", "CC="+str(clang),
                               "opt="+" ".join(target_opts), "crafty-make"]
            run(crafty_make)

    def run_tests(self, runner):
        with local.cwd(self.src_dir):
            exp = wrap("./crafty", self)
            runner((cat[path.join(self.testdir, "test1.sh")] | exp),
                retcode=[0, 120])
            runner((cat[path.join(self.testdir, "test2.sh")] | exp),
                retcode=[0, 120])
