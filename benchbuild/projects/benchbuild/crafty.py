from benchbuild.environments import container
from benchbuild.project import Project
from benchbuild.source import HTTP
from benchbuild.utils.cmd import cat, make, mkdir, mv, unzip


class Crafty(Project):
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
    CONTAINER = container.Buildah().from_('debian:buster-slim')

    def compile(self):
        crafty_source = local.path(self.source_of('crafty.zip'))
        book_source = local.path(self.source_of('inputs.tar.gz'))

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
        unpack_dir = local.path('crafty.src')
        test_source = local.path(self.source_of('inputs.tar.gz'))

        with local.cwd(unpack_dir):
            crafty = wrapping.wrapping.wrap("./crafty", self)
            test1 = run.watch((cat[test_source / "test1.sh"] | crafty))
            test2 = run.watch((cat[test_source / "test2.sh"] | crafty))

            test1(retcode=[0, 120])
            test2(retcode=[0, 120])
