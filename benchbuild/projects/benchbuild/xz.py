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
            with local.env(CC=str(clang)):
                run.run(configure["--enable-threads=no", "--with-gnu-ld=yes",
                                  "--disable-shared",
                                  "--disable-dependency-tracking",
                                  "--disable-xzdec", "--disable-lzmadec",
                                  "--disable-lzmainfo", "--disable-lzma-links",
                                  "--disable-scripts", "--disable-doc"])

            run.run(make["CC=" + str(clang), "clean", "all"])

    def run_tests(self, runner):
        unpack_dir = local.path('xz-{0}'.format(self.version))
        _xz = wrapping.wrap(unpack_dir / "src" / "xz" / "xz", self)

        # Compress
        runner(_xz["--compress", "-f", "-k", "-e", "-9", "text.html"])
        runner(_xz["--compress", "-f", "-k", "-e", "-9", "chicken.jpg"])
        runner(_xz["--compress", "-f", "-k", "-e", "-9", "control"])
        runner(_xz["--compress", "-f", "-k", "-e", "-9", "input.source"])
        runner(_xz["--compress", "-f", "-k", "-e", "-9", "liberty.jpg"])

        # Decompress
        runner(_xz["--decompress", "-f", "-k", "text.html.xz"])
        runner(_xz["--decompress", "-f", "-k", "chicken.jpg.xz"])
        runner(_xz["--decompress", "-f", "-k", "control.xz"])
        runner(_xz["--decompress", "-f", "-k", "input.source.xz"])
        runner(_xz["--decompress", "-f", "-k", "liberty.jpg.xz"])
