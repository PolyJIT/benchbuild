from plumbum import local

import benchbuild as bb
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.source import HTTP, Git
from benchbuild.utils.cmd import make, tar


class Bzip2(bb.Project):
    """ Bzip2 """

    NAME = 'bzip2'
    DOMAIN = 'compression'
    GROUP = 'benchbuild'
    SOURCE = [
        Git(
            remote='https://github.com/PolyJIT/bzip2',
            local='bzip2.git',
            limit=1,
            refspec='HEAD'
        ),
        HTTP(
            remote={'1.0': 'http://lairosiel.de/dist/compression.tar.gz'},
            local='compression.tar.gz'
        )
    ]

    CONTAINER = ContainerImage() \
        .from_('benchbuild:alpine') \
        .run('apk', 'add', 'make')

    def compile(self):
        bzip2_repo = local.path(self.source_of('bzip2.git'))
        compression_source = local.path(self.source_of('compression.tar.gz'))
        tar('xf', compression_source)

        clang = bb.compiler.cc(self)
        with local.cwd(bzip2_repo):
            make_ = bb.watch(make)
            make_("CFLAGS=-O3", "CC=" + str(clang), "clean", "bzip2")

    def run_tests(self):
        bzip2_repo = local.path(self.source_of('bzip2.git'))
        bzip2 = bb.wrap(bzip2_repo / "bzip2", self)
        _bzip2 = bb.watch(bzip2)

        # Compress
        _bzip2("-f", "-z", "-k", "--best", "compression/text.html")
        _bzip2("-f", "-z", "-k", "--best", "compression/chicken.jpg")
        _bzip2("-f", "-z", "-k", "--best", "compression/control")
        _bzip2("-f", "-z", "-k", "--best", "compression/input.source")
        _bzip2("-f", "-z", "-k", "--best", "compression/liberty.jpg")

        # Decompress
        _bzip2("-f", "-k", "--decompress", "compression/text.html.bz2")
        _bzip2("-f", "-k", "--decompress", "compression/chicken.jpg.bz2")
        _bzip2("-f", "-k", "--decompress", "compression/control.bz2")
        _bzip2("-f", "-k", "--decompress", "compression/input.source.bz2")
        _bzip2("-f", "-k", "--decompress", "compression/liberty.jpg.bz2")
