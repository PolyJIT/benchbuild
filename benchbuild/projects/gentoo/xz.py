"""
xz experiment within gentoo chroot.
"""
from plumbum import local

from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils import download, wrapping
from benchbuild.utils.cmd import tar


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
        download.Wget(test_url, test_archive)
        tar("fxz", test_archive)

    def run_tests(self, runner):
        xz = wrapping.wrap(local.path("/usr/bin/xz"), self)

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
