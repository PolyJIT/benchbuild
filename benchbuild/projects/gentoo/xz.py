"""
xz experiment within gentoo chroot.
"""
from plumbum import local

from benchbuild.projects.gentoo.gentoo import GentooGroup
from benchbuild.utils import download, run, wrapping
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

    def run_tests(self):
        xz = wrapping.wrap(local.path("/usr/bin/xz"), self)
        xz = run.watch(xz)

        # Compress
        xz("--compress", "-f", "-k", "-e", "-9", "compression/text.html")
        xz("--compress", "-f", "-k", "-e", "-9", "compression/chicken.jpg")
        xz("--compress", "-f", "-k", "-e", "-9", "compression/control")
        xz("--compress", "-f", "-k", "-e", "-9", "compression/input.source")
        xz("--compress", "-f", "-k", "-e", "-9", "compression/liberty.jpg")

        # Decompress
        xz("--decompress", "-f", "-k", "compression/text.html.xz")
        xz("--decompress", "-f", "-k", "compression/chicken.jpg.xz")
        xz("--decompress", "-f", "-k", "compression/control.xz")
        xz("--decompress", "-f", "-k", "compression/input.source.xz")
        xz("--decompress", "-f", "-k", "compression/liberty.jpg.xz")
