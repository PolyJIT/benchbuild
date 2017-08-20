from os import path
from benchbuild.utils.wrapping import wrap
from benchbuild.projects.benchbuild.group import BenchBuildGroup
from benchbuild.utils.compiler import lt_clang
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import run
from benchbuild.utils.cmd import cat, make, unzip, mv, mkdir
from plumbum import local


class Crafty(BenchBuildGroup):
    """ crafty benchmark """

    NAME = 'crafty'
    DOMAIN = 'scientific'
    VERSION = '25.2'

    src_dir = "crafty-{0}".format(VERSION)
    src_uri = "http://www.craftychess.com/downloads/source/crafty-{0}.zip".format(VERSION)
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
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        with local.cwd(self.src_dir):
            target_opts = ["-DCPUS=1", "-DSYZYGY", "-DTEST"]
            crafty_make = make["target=UNIX", "CC="+str(clang),
                               "opt="+" ".join(target_opts), "crafty-make"]
            run(crafty_make)

    def run_tests(self, experiment, run):
        with local.cwd(self.src_dir):
            exp = wrap("./crafty", experiment)
            run((cat[path.join(self.testdir, "test1.sh")] | exp), retcode=120)
            run((cat[path.join(self.testdir, "test2.sh")] | exp), retcode=120)
