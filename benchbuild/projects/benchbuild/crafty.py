from plumbum import local

from benchbuild import project
from benchbuild.downloads import HTTP
from benchbuild.downloads.versions import product
from benchbuild.utils import compiler, run, wrapping
from benchbuild.utils.cmd import cat, make, mkdir, mv, unzip


class Crafty(project.Project):
    """ crafty benchmark """

    NAME = 'crafty'
    DOMAIN = 'scientific'
    GROUP = 'benchbuild'
    VERSION = '25.2'
    SOURCE = [
        HTTP(remote={
            '25.2':
            'http://www.craftychess.com/downloads/source/crafty-25.2.zip'
        },
             local='crafty.zip'),
        HTTP(remote={
            '1.0': 'http://www.craftychess.com/downloads/book/book.bin'
        },
             local='book.bin')
    ]
    VARIANTS = product(*SOURCE)

    def compile(self):
        crafty_source = local.path(self.source[0].local)
        book_source = local.path(self.source[1].local)

        unpack_dir = "crafty.src"
        mkdir(unpack_dir)

        with local.cwd(unpack_dir):
            unzip(crafty_source)
        mv(book_source, unpack_dir)

        clang = compiler.cc(self)
        with local.cwd(unpack_dir):
            target_opts = ["-DCPUS=1", "-DSYZYGY", "-DTEST"]
            make_ = run.watch(make)
            make_("target=UNIX", "CC=" + str(clang),
                  "opt=" + " ".join(target_opts), "crafty-make")

    def run_tests(self):
        unpack_dir = "crafty.src"
        with local.cwd(unpack_dir):
            crafty = wrapping.wrap("./crafty", self)
            testdir = local.path(self.testdir)
            test1 = run.watch((cat[testdir / "test1.sh"] | crafty))
            test2 = run.watch((cat[testdir / "test2.sh"] | crafty))

            test1(retcode=[0, 120])
            test2(retcode=[0, 120])
