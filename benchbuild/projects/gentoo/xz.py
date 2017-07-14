"""
xz experiment within gentoo chroot.
"""
from os import path
from benchbuild.utils.wrapping import wrap_in_uchroot as wrap
from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils.downloader import Wget
from benchbuild.utils.run import uretry, uchroot
from benchbuild.utils.cmd import tar  # pylint: disable=E0401


run = uretry


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
        Wget(test_url, test_archive)
        tar("fxz", test_archive)

    def build(self):
        emerge_in_chroot = uchroot()["/usr/bin/emerge"]
        run(emerge_in_chroot["app-arch/xz-utils"])

    def run_tests(self, experiment, run):
        wrap(
            path.join(self.builddir, "usr", "bin", "xz"), experiment,
            self.builddir)
        xz = uchroot()["/usr/bin/xz"]

        # Compress
        run(xz["--compress", "-f", "-k", "-e", "-9", "compression/text.html"])
        run(xz["--compress", "-f", "-k", "-e", "-9",
               "compression/chicken.jpg"])
        run(xz["--compress", "-f", "-k", "-e", "-9", "compression/control"])
        run(xz["--compress", "-f", "-k", "-e", "-9",
               "compression/input.source"])
        run(xz["--compress", "-f", "-k", "-e", "-9",
               "compression/liberty.jpg"])

        # Decompress
        run(xz["--decompress", "-f", "-k", "compression/text.html.xz"])
        run(xz["--decompress", "-f", "-k", "compression/chicken.jpg.xz"])
        run(xz["--decompress", "-f", "-k", "compression/control.xz"])
        run(xz["--decompress", "-f", "-k", "compression/input.source.xz"])
        run(xz["--decompress", "-f", "-k", "compression/liberty.jpg.xz"])
