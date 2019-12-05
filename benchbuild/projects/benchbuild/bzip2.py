from plumbum import local

from benchbuild import project
from benchbuild.downloads import Git, HTTP
from benchbuild.downloads.versions import product
from benchbuild.utils.cmd import cp, make, tar
from benchbuild.utils import compiler, run, wrapping



class Bzip2(project.Project):
    """ Bzip2 """

    VERSION = 'HEAD'
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
    VARIANTS = product(*SOURCE)

    def compile(self):
        bzip2_repo = self.variant['bzip2.git'].owner.local
        compression_source = local.path(self.source[1].local)
        tar('xf', compression_source)

        clang = compiler.cc(self)
        with local.cwd(bzip2_repo):
            make_ = run.watch(make)
            make_("CFLAGS=-O3", "CC=" + str(clang), "clean", "bzip2")

    def run_tests(self):
        bzip2_repo = local.path(self.source[0].local)
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
