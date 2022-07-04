from plumbum import local

import benchbuild as bb
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.settings import CFG
from benchbuild.source import HTTP
from benchbuild.utils.cmd import make, tar
from benchbuild.utils.settings import get_number_of_jobs


class Gzip(bb.Project):
    """ Gzip """

    NAME = 'gzip'
    DOMAIN = 'compression'
    GROUP = 'benchbuild'
    SOURCE = [
        HTTP(
            remote={'1.6': 'http://ftpmirror.gnu.org/gzip/gzip-1.6.tar.xz'},
            local='gzip.tar.xz'
        ),
        HTTP(
            remote={'1.0': 'http://lairosiel.de/dist/compression.tar.gz'},
            local='compression.tar.gz'
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def compression_test(self):
        gzip_version = self.version_of('gzip.tar.xz')
        unpack_dir = local.path(f'gzip-{gzip_version}.tar.xz')
        _gzip = bb.watch(bb.wrap(unpack_dir / "gzip", self))

        # Compress
        _gzip("-f", "-k", "--best", "compression/text.html")
        _gzip("-f", "-k", "--best", "compression/chicken.jpg")
        _gzip("-f", "-k", "--best", "compression/control")
        _gzip("-f", "-k", "--best", "compression/input.source")
        _gzip("-f", "-k", "--best", "compression/liberty.jpg")

        # Decompress
        _gzip("-f", "-k", "--decompress", "compression/text.html.gz")
        _gzip("-f", "-k", "--decompress", "compression/chicken.jpg.gz")
        _gzip("-f", "-k", "--decompress", "compression/control.gz")
        _gzip("-f", "-k", "--decompress", "compression/input.source.gz")
        _gzip("-f", "-k", "--decompress", "compression/liberty.jpg.gz")

    def compile_project(self):
        gzip_source = local.path(self.source_of('gzip.tar.xz'))
        compression_source = local.path(self.source_of('compression.tar.gz'))

        tar('xfJ', gzip_source)
        tar('xf', compression_source)

        gzip_version = self.version_of('gzip.tar.xz')
        unpack_dir = "gzip-{0}.tar.xz".format(gzip_version)

        clang = bb.compiler.cc(self)
        with local.cwd(unpack_dir):
            _configure = bb.watch(local["./configure"])
            with local.env(CC=str(clang)):
                _configure(
                    "--disable-dependency-tracking", "--disable-silent-rules",
                    "--with-gnu-ld"
                )
            _make = bb.watch(make)
            _make("-j" + str(get_number_of_jobs(CFG)), "clean", "all")
