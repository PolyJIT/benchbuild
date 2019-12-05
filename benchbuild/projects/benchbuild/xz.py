from plumbum import local

from benchbuild import project
from benchbuild.downloads import HTTP
from benchbuild.downloads.versions import product
from benchbuild.utils import compiler, run, wrapping
from benchbuild.utils.cmd import cp, make, tar


class XZ(project.Project):
    """ XZ """
    VERSION = '5.2.1'
    NAME: str = 'xz'
    DOMAIN: str = 'compression'
    GROUP: str = 'benchbuild'

    SOURCE = [
        HTTP(remote={'5.2.1', 'http://tukaani.org/xz/xz-5.2.1.tar.gz'},
             local='xz.tar.gz'),
        HTTP(remote={'1.0': 'http://lairosiel.de/dist/compression.tar.gz'},
             local='compression.tar.gz')
    ]
    VARIANTS = product(*SOURCE)

    def compile(self):
        xz_source = local.path(self.source[0].local)
        compression_source = local.path(self.source[1].local)

        tar('xf', xz_source)
        tar('xf', compression_source)

        unpack_dir = local.path('xz-{0}'.format(self.version))
        clang = compiler.cc(self)
        with local.cwd(unpack_dir):
            configure = local["./configure"]
            configure = run.watch(configure)
            with local.env(CC=str(clang)):
                configure("--enable-threads=no", "--with-gnu-ld=yes",
                          "--disable-shared", "--disable-dependency-tracking",
                          "--disable-xzdec", "--disable-lzmadec",
                          "--disable-lzmainfo", "--disable-lzma-links",
                          "--disable-scripts", "--disable-doc")

            make_ = run.watch(make)
            make_("CC=" + str(clang), "clean", "all")

    def run_tests(self):
        unpack_dir = local.path('xz-{0}'.format(self.version))
        _xz = wrapping.wrap(unpack_dir / "src" / "xz" / "xz", self)
        _xz = run.watch(_xz)

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
