"""
xz experiment within gentoo chroot.
"""
from plumbum import local

from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils.cmd import tar
from benchbuild.utils.downloader import Wget
from benchbuild.utils.uchroot import uchroot, uretry
from benchbuild.utils.wrapping import wrap_in_uchroot as wrap


class XZ(GentooGroup):
    """
        app-arch/xz
    """
    NAME = "xz"
    DOMAIN = "app-arch"

    test_url = "http://lairosiel.de/dist/"
    test_archive = "compression.tar.gz"
    testfiles = [
        "text.html", "chicken.jpg", "control", "input.source", "liberty.jpg"
    ]

    def compile(self):
        super(XZ, self).compile()

        test_archive = self.test_archive
        test_url = self.test_url + test_archive
        Wget(test_url, test_archive)
        tar("fxz", test_archive)

        emerge_in_chroot = uchroot()["/usr/bin/emerge"]
        uretry(emerge_in_chroot["app-arch/xz-utils"])

    def run_tests(self, runner):
        xz_bin = local.cwd / "usr" / "bin" / "xz"
        wrap(xz_bin, self, self.builddir)
        xz = uchroot()["/usr/bin/xz"]

        # Compress
        runner(
            xz["--compress", "-f", "-k", "-e", "-9", "compression/text.html"])
        runner(xz["--compress", "-f", "-k", "-e", "-9",
                  "compression/chicken.jpg"])
        runner(xz["--compress", "-f", "-k", "-e", "-9", "compression/control"])
        runner(xz["--compress", "-f", "-k", "-e", "-9",
                  "compression/input.source"])
        runner(xz["--compress", "-f", "-k", "-e", "-9",
                  "compression/liberty.jpg"])

        # Decompress
        runner(xz["--decompress", "-f", "-k", "compression/text.html.xz"])
        runner(xz["--decompress", "-f", "-k", "compression/chicken.jpg.xz"])
        runner(xz["--decompress", "-f", "-k", "compression/control.xz"])
        runner(xz["--decompress", "-f", "-k", "compression/input.source.xz"])
        runner(xz["--decompress", "-f", "-k", "compression/liberty.jpg.xz"])
