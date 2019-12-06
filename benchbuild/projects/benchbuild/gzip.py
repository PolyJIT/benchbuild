from plumbum import local

import benchbuild as bb

from benchbuild.downloads import HTTP
from benchbuild.settings import CFG
from benchbuild.utils.cmd import cp, make, tar


class Gzip(bb.Project):
    """ Gzip """

    NAME: str = 'gzip'
    DOMAIN: str = 'compression'
    GROUP: str = 'benchbuild'
    SOURCE = [
        HTTP(remote={'1.6': 'http://ftpmirror.gnu.org/gzip/gzip-1.6.tar.xz'},
             local='gzip.tar.xz'),
        HTTP(remote={'1.0': 'http://lairosiel.de/dist/compression.tar.gz'},
             local='compression.tar.gz')
    ]

    def run_tests(self):
        gzip_version = self.version_of('gzip.tar.xz')
        unpack_dir = bb.path(f'gzip-{gzip_version}.tar.xz')

        gzip = bb.wrap(unpack_dir / "gzip", self)
        gzip = bb.watch(gzip)

        # Compress
        gzip("-f", "-k", "--best", "compression/text.html")
        gzip("-f", "-k", "--best", "compression/chicken.jpg")
        gzip("-f", "-k", "--best", "compression/control")
        gzip("-f", "-k", "--best", "compression/input.source")
        gzip("-f", "-k", "--best", "compression/liberty.jpg")

        # Decompress
        gzip("-f", "-k", "--decompress", "compression/text.html.gz")
        gzip("-f", "-k", "--decompress", "compression/chicken.jpg.gz")
        gzip("-f", "-k", "--decompress", "compression/control.gz")
        gzip("-f", "-k", "--decompress", "compression/input.source.gz")
        gzip("-f", "-k", "--decompress", "compression/liberty.jpg.gz")

    def compile(self):
        gzip_source = bb.path(self.source_of('gzip.tar.xz'))
        compression_source = bb.path(self.source_of('compression.tar.gz'))

        tar('xfJ', gzip_source)
        tar('xf', compression_source)

        gzip_version = self.version_of('gzip.tar.xz')
        unpack_dir = "gzip-{0}.tar.xz".format(gzip_version)

        clang = bb.compiler.cc(self)
        with bb.cwd(unpack_dir):
            configure = local["./configure"]
            configure = bb.watch(configure)
            with bb.env(CC=str(clang)):
                configure("--disable-dependency-tracking",
                          "--disable-silent-rules", "--with-gnu-ld")
            make_ = bb.watch(make)
            make_("-j" + str(CFG["jobs"]), "clean", "all")
