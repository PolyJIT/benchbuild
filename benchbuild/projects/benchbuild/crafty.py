import benchbuild as bb
from benchbuild.utils import download
from benchbuild.utils.cmd import cat, make, mkdir, mv, unzip


@download.with_wget(
    {"25.2": "http://www.craftychess.com/downloads/source/crafty-25.2.zip"})
class Crafty(bb.Project):
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

        mv(book_file, unpack_dir)
        with bb.cwd(unpack_dir):
            unzip(bb.path("..") / self.src_file)

        clang = bb.compiler.cc(self)
        with bb.cwd(unpack_dir):
            target_opts = ["-DCPUS=1", "-DSYZYGY", "-DTEST"]
            _make = bb.watch(make)
            _make("target=UNIX", "CC=" + str(clang),
                  "opt=" + " ".join(target_opts), "crafty-make")

    def run_tests(self):
        testdir = bb.path(self.testdir)

        with bb.cwd(testdir):
            crafty = bb.wrap("./crafty", self)
            _test1 = bb.watch((cat[test_source / "test1.sh"] | crafty))
            _test2 = bb.watch((cat[test_source / "test2.sh"] | crafty))

            _test1(retcode=[0, 120])
            _test2(retcode=[0, 120])
