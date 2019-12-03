from plumbum import local

from benchbuild import project
from benchbuild.downloads import HTTP
from benchbuild.downloads.versions import product
from benchbuild.settings import CFG
from benchbuild.utils import compiler, run, wrapping
from benchbuild.utils.cmd import cp, make, tar


class Gzip(project.Project):
    """ Gzip """

    NAME = 'gzip'
    DOMAIN = 'compression'
    GROUP = 'benchbuild'
    VERSION = '1.6'
    SOURCE = [
        HTTP(remote={'1.6': 'http://ftpmirror.gnu.org/gzip/gzip-1.6.tar.xz'},
             local='gzip.tar.xz'),
        HTTP(remote={'1.0': 'http://lairosiel.de/dist/compression.tar.gz'},
             local='compression.tar.gz')
    ]
    VARIANTS = product(*SOURCE)

    def run_tests(self):
        unpack_dir = local.path("gzip-{0}.tar.xz".format(self.version))
        gzip = wrapping.wrap(unpack_dir / "gzip", self)
        gzip = run.watch(gzip)

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
        gzip_source = local.path(self.source[0].local)
        compression_source = local.path(self.source[1].local)
        tar('xfJ', gzip_source)
        tar('xf', compression_source)

        unpack_dir = "gzip-{0}.tar.xz".format(self.version)

        clang = compiler.cc(self)
        with local.cwd(unpack_dir):
            configure = local["./configure"]
            configure = run.watch(configure)
            with local.env(CC=str(clang)):
                configure("--disable-dependency-tracking",
                          "--disable-silent-rules", "--with-gnu-ld")
            make_ = run.watch(make)
            make_("-j" + str(CFG["jobs"]), "clean", "all")
