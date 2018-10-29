from plumbum import local

from benchbuild import project
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import cat, make, mkdir, mv, unzip


@download.with_wget({
    "25.2":
    "http://www.craftychess.com/downloads/source/crafty-25.2.zip"
})
class Crafty(project.Project):
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
        download.Wget(book_bin, book_file)

        unpack_dir = "crafty.src"
        mkdir(unpack_dir)

        with local.cwd(unpack_dir):
            unzip(local.path("..") / self.src_file)
        mv(book_file, unpack_dir)

        clang = compiler.cc(self)
        with local.cwd(unpack_dir):
            target_opts = ["-DCPUS=1", "-DSYZYGY", "-DTEST"]
            crafty_make = make["target=UNIX", "CC=" + str(clang), "opt=" +
                               " ".join(target_opts), "crafty-make"]
            run.run(crafty_make)

    def run_tests(self, runner):
        unpack_dir = "crafty.src"
        with local.cwd(unpack_dir):
            crafty = wrapping.wrap("./crafty", self)
            testdir = local.path(self.testdir)
            runner((cat[testdir / "test1.sh"] | crafty), retcode=[0, 120])
            runner((cat[testdir / "test2.sh"] | crafty), retcode=[0, 120])
