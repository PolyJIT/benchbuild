"""
xz experiment within gentoo chroot.
"""
from os import path
from pprof.projects.gentoo.gentoo import GentooGroup
from pprof.utils.downloader import Wget
from pprof.utils.run import run, uchroot
from plumbum import local
from plumbum.cmd import tar  # pylint: disable=E0401


class XZ(GentooGroup):
    """
        app-arch/xz
    """
    NAME = "gentoo-xz"
    DOMAIN = "app-arch"

    test_url = "http://lairosiel.de/dist/"
    test_archive = "compression.tar.gz"
    testfiles = ["text.html", "chicken.jpg", "control", "input.source",
                 "liberty.jpg"]

    def prepare(self):
        super(XZ, self).prepare()

        test_archive = self.test_archive
        test_url = self.test_url + test_archive
        with local.cwd(self.builddir):
            Wget(test_url, test_archive)
            tar("fxz", test_archive)

    def build(self):
        with local.cwd(self.builddir):
            emerge_in_chroot = uchroot()["/usr/bin/emerge"]
            run(emerge_in_chroot["app-arch/xz-utils"])

    def run_tests(self, experiment):
        from pprof.project import wrap

        wrap(path.join(self.builddir, "usr", "bin", "xz"), experiment,
             self.builddir)
        xz = uchroot()["/usr/bin/xz"]

        # Compress
        run(xz["--compress", "-f", "-k", "-e", "-9", "compression/text.html"])
        run(xz["--compress", "-f", "-k", "-e", "-9", "compression/chicken.jpg"])
        run(xz["--compress", "-f", "-k", "-e", "-9", "compression/control"])
        run(xz["--compress", "-f", "-k", "-e", "-9", "compression/input.source"])
        run(xz["--compress", "-f", "-k", "-e", "-9", "compression/liberty.jpg"])

        # Decompress
        run(xz["--decompress", "-f", "-k", "compression/text.html.xz"])
        run(xz["--decompress", "-f", "-k", "compression/chicken.jpg.xz"])
        run(xz["--decompress", "-f", "-k", "compression/control.xz"])
        run(xz["--decompress", "-f", "-k", "compression/input.source.xz"])
        run(xz["--decompress", "-f", "-k", "compression/liberty.jpg.xz"])

