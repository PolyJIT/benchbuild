from plumbum import local

from benchbuild import project
from benchbuild.utils import compiler, download, run, wrapping
from benchbuild.utils.cmd import cp, make, tar


@download.with_wget({'5.2.1': 'http://tukaani.org/xz/xz-5.2.1.tar.gz'})
class XZ(project.Project):
    """ XZ """
    NAME = 'xz'
    DOMAIN = 'compression'
    GROUP = 'benchbuild'
    VERSION = '5.2.1'
    SRC_FILE = 'xz.tar.gz'

    testfiles = [
        "text.html", "chicken.jpg", "control", "input.source", "liberty.jpg"
    ]

    def compile(self):
        self.download()

        tar('xfz', self.src_file)

        test_dir = local.path(self.testdir)
        testfiles = [test_dir / x for x in self.testfiles]
        cp(testfiles, self.builddir)

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
        _xz("--compress", "-f", "-k", "-e", "-9", "text.html")
        _xz("--compress", "-f", "-k", "-e", "-9", "chicken.jpg")
        _xz("--compress", "-f", "-k", "-e", "-9", "control")
        _xz("--compress", "-f", "-k", "-e", "-9", "input.source")
        _xz("--compress", "-f", "-k", "-e", "-9", "liberty.jpg")

        # Decompress
        _xz("--decompress", "-f", "-k", "text.html.xz")
        _xz("--decompress", "-f", "-k", "chicken.jpg.xz")
        _xz("--decompress", "-f", "-k", "control.xz")
        _xz("--decompress", "-f", "-k", "input.source.xz")
        _xz("--decompress", "-f", "-k", "liberty.jpg.xz")
