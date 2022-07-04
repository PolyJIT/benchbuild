from plumbum import local

import benchbuild as bb
from benchbuild import CFG
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.source import HTTP
from benchbuild.utils.cmd import make, tar


class XZ(bb.Project):
    """ XZ """
    VERSION = '5.2.1'
    NAME = 'xz'
    DOMAIN = 'compression'
    GROUP = 'benchbuild'

    SOURCE = [
        HTTP(
            remote={'5.2.1': 'http://tukaani.org/xz/xz-5.2.1.tar.gz'},
            local='xz.tar.gz'
        ),
        HTTP(
            remote={'1.0': 'http://lairosiel.de/dist/compression.tar.gz'},
            local='compression.tar.gz'
        )
    ]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def compile(self):
        xz_source = local.path(self.source_of('xz.tar.gz'))
        xz_version = self.version_of('xz.tar.gz')
        compression_source = local.path(self.source_of('compression.tar.gz'))

        tar('xf', xz_source)
        tar('xf', compression_source)

        unpack_dir = local.path(f'xz-{xz_version}')
        clang = bb.compiler.cc(self)
        with local.cwd(unpack_dir):
            configure = local["./configure"]
            _configure = bb.watch(configure)
            with local.env(CC=str(clang)):
                _configure(
                    "--enable-threads=no", "--with-gnu-ld=yes",
                    "--disable-shared", "--disable-dependency-tracking",
                    "--disable-xzdec", "--disable-lzmadec",
                    "--disable-lzmainfo", "--disable-lzma-links",
                    "--disable-scripts", "--disable-doc"
                )

            _make = bb.watch(make)
            _make("CC=" + str(clang), "clean", "all")

    def run_tests(self):
        xz_version = self.version_of('xz.tar.gz')
        unpack_dir = local.path(f'xz-{xz_version}')
        xz = bb.wrap(unpack_dir / "src" / "xz" / "xz", self)
        _xz = bb.watch(xz)

        # Compress
        _xz("--compress", "-f", "-k", "-e", "-9", "compression/text.html")
        _xz("--compress", "-f", "-k", "-e", "-9", "compression/chicken.jpg")
        _xz("--compress", "-f", "-k", "-e", "-9", "compression/control")
        _xz("--compress", "-f", "-k", "-e", "-9", "compression/input.source")
        _xz("--compress", "-f", "-k", "-e", "-9", "compression/liberty.jpg")

        # Decompress
        _xz("--decompress", "-f", "-k", "compression/text.html.xz")
        _xz("--decompress", "-f", "-k", "compression/chicken.jpg.xz")
        _xz("--decompress", "-f", "-k", "compression/control.xz")
        _xz("--decompress", "-f", "-k", "compression/input.source.xz")
        _xz("--decompress", "-f", "-k", "compression/liberty.jpg.xz")
