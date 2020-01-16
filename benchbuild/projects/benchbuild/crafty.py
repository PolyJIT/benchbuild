import benchbuild as bb

from benchbuild.source import HTTP
from benchbuild.utils.cmd import cat, make, mkdir, mv, unzip


class Crafty(bb.Project):
    """ crafty benchmark """

    NAME: str = 'crafty'
    DOMAIN: str = 'scientific'
    GROUP: str = 'benchbuild'
    SOURCE = [
        HTTP(remote={
            '25.2':
            'http://www.craftychess.com/downloads/source/crafty-25.2.zip'
        },
             local='crafty.zip'),
        HTTP(remote={
            '1.0': 'http://www.craftychess.com/downloads/book/book.bin'
        },
             local='book.bin'),
        HTTP(remote={
            '2016-11-crafty.tar.gz':
            'http://lairosiel.de/dist/2016-11-crafty.tar.gz'
        },
             local='inputs.tar.gz')
    ]

    def compile(self):
        crafty_source = bb.path(self.source_of('crafty.zip'))
        book_source = bb.path(self.source_of('inputs.tar.gz'))

        unpack_dir = "crafty.src"
        mkdir(unpack_dir)

        with bb.cwd(unpack_dir):
            unzip(crafty_source)
        mv(book_source, unpack_dir)

        clang = bb.compiler.cc(self)
        with bb.cwd(unpack_dir):
            target_opts = ["-DCPUS=1", "-DSYZYGY", "-DTEST"]
            make_ = bb.run.watch(make)
            make_("target=UNIX", "CC=" + str(clang),
                  "opt=" + " ".join(target_opts), "crafty-make")

    def run_tests(self):
        unpack_dir = bb.path('crafty.src')
        test_source = bb.path(self.source_of('inputs.tar.gz'))

        with bb.cwd(unpack_dir):
            crafty = bb.wrapping.wrap("./crafty", self)
            test1 = bb.run.watch((cat[test_source / "test1.sh"] | crafty))
            test2 = bb.run.watch((cat[test_source / "test2.sh"] | crafty))

            test1(retcode=[0, 120])
            test2(retcode=[0, 120])
