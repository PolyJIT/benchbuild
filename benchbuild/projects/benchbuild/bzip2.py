from benchbuild.project import Project
from benchbuild.source import Git, HTTP
from benchbuild.utils.cmd import make, tar

from benchbuild.environments import Buildah


class Bzip2(Project):
    """ Bzip2 """

    NAME: str = 'bzip2'
    DOMAIN: str = 'compression'
    GROUP: str = 'benchbuild'
    SOURCE = [
        Git(remote='https://github.com/PolyJIT/bzip2',
            local='bzip2.git',
            limit=1,
            refspec='HEAD'),
        HTTP(remote={'1.0': 'http://lairosiel.de/dist/compression.tar.gz'},
             local='compression.tar.gz')
    ]

    CONTAINER: Buildah = Buildah().from_('python:3.7-buster')

    def compile(self):
        bzip2_repo = self.source_of('bzip2.git')
        compression_source = self.source_of('compression.tar.gz')

        tar('xf', compression_source)
        clang = compiler.cc(self)
        with local.cwd(bzip2_repo):
            make_ = run.watch(make)
            make_("CFLAGS=-O3", "CC=" + str(clang), "clean", "bzip2")

    def run_tests(self):
        bzip2_repo = local.path(self.source_of('bzip2.git'))
        bzip2 = wrapping.wrap(bzip2_repo / "bzip2", self)
        bzip2 = run.watch(bzip2)

        # Compress
        bzip2("-f", "-z", "-k", "--best", "compression/text.html")
        bzip2("-f", "-z", "-k", "--best", "compression/chicken.jpg")
        bzip2("-f", "-z", "-k", "--best", "compression/control")
        bzip2("-f", "-z", "-k", "--best", "compression/input.source")
        bzip2("-f", "-z", "-k", "--best", "compression/liberty.jpg")

        # Decompress
        bzip2("-f", "-k", "--decompress", "compression/text.html.bz2")
        bzip2("-f", "-k", "--decompress", "compression/chicken.jpg.bz2")
        bzip2("-f", "-k", "--decompress", "compression/control.bz2")
        bzip2("-f", "-k", "--decompress", "compression/input.source.bz2")
        bzip2("-f", "-k", "--decompress", "compression/liberty.jpg.bz2")
