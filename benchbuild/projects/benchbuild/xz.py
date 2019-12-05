from plumbum import local

import benchbuild as bb

from benchbuild.downloads import HTTP
from benchbuild.utils.cmd import cp, make, tar


class XZ(bb.Project):
    """ XZ """

    NAME: str = 'xz'
    DOMAIN: str = 'compression'
    GROUP: str = 'benchbuild'
    VERSION: str = '5.2.1'

    SOURCE = [
        HTTP(remote={'5.2.1', 'http://tukaani.org/xz/xz-5.2.1.tar.gz'},
             local='xz.tar.gz'),
        HTTP(remote={'1.0': 'http://lairosiel.de/dist/compression.tar.gz'},
             local='compression.tar.gz')
    ]

    def compile(self):
        xz_source = bb.path(self.source_of('xz.tar.gz'))
        compression_source = bb.path(self.source_of('compression.tar.gz'))

        tar('xf', xz_source)
        tar('xf', compression_source)

        unpack_dir = bb.path('xz-{0}'.format(self.version))
        clang = bb.compiler.cc(self)
        with bb.cwd(unpack_dir):
            configure = local["./configure"]
            configure = bb.watch(configure)
            with bb.env(CC=str(clang)):
                configure("--enable-threads=no", "--with-gnu-ld=yes",
                          "--disable-shared", "--disable-dependency-tracking",
                          "--disable-xzdec", "--disable-lzmadec",
                          "--disable-lzmainfo", "--disable-lzma-links",
                          "--disable-scripts", "--disable-doc")

            make_ = bb.watch(make)
            make_("CC=" + str(clang), "clean", "all")

    def run_tests(self):
        unpack_dir = local.path('xz-{0}'.format(self.version))
        _xz = bb.wrap(unpack_dir / "src" / "xz" / "xz", self)
        _xz = bb.watch(_xz)

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
